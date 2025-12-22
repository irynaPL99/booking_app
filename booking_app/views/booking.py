from django.utils import timezone
from datetime import timedelta

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from booking_app.choices import Role
from booking_app.choices import BookingStatus
from booking_app.models import Booking
from booking_app.serializers.booking import BookingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    """API for guest bookings. Only own bookings visible."""

    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def get_queryset(self):
        """Return bookings visible to the current authenticated user
        (guests see their own bookings, owners see bookings for their listings).
        """

        user = self.request.user

        # Владелец жилья видит брони на свои объявления
        if getattr(user, "role", None) == Role.OWNER:
            return Booking.objects.filter(listing__owner=user)

        # Гость видит только свои брони
        return Booking.objects.filter(guest=user)

    def perform_create(self, serializer):
        """Set current user as booking guest."""
        serializer.save(guest=self.request.user)

    # GET /api/v1/bookings/owner/ — список всех броней на СВОИ объявления (для OWNER)
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="owner",
    )
    def owner_bookings(self, request):
        """List bookings for listings owned by current user (owner)."""
        user = request.user
        if getattr(user, "role", None) != Role.OWNER:
            return Response(
                {"detail": "Only owners can see bookings for their listings."},
                status=status.HTTP_403_FORBIDDEN,
            )

        qs = Booking.objects.filter(listing__owner=user).order_by("-check_in")
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    # action для смены статуса, PATCH /api/v1/bookings/{id}/set-status/ (+ Token)
    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="set-status",
    )
    def set_status(self, request, pk=None):
        """Allow owner to confirm or rejected, or cancel a booking."""
        booking = self.get_object()
        user = request.user

        # Только хозяин объявления может менять статус
        if booking.listing.owner != user:
            return Response(
                {"detail": "Only listing owner can change booking status."},
                status=status.HTTP_403_FORBIDDEN,
            )

        new_status = request.data.get("status")
        # допустимые статусы для хозяина
        allowed_statuses = {
            "confirmed": BookingStatus.CONFIRMED,
            "rejected": BookingStatus.REJECTED,
            "cancelled_by_owner": BookingStatus.CANCELLED_BY_OWNER,
        }

        if new_status not in allowed_statuses:
            return Response(
                {"detail": "Invalid status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = allowed_statuses[new_status]
        booking.save(update_fields=["status"])

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    # ограничения для гостя при PATCH:
    def perform_update(self, serializer):
        """Allow guest to edit only own pending bookings."""
        instance = self.get_object()
        user = self.request.user

        # Только гость может редактировать свою бронь
        if instance.guest != user:
            raise ValidationError("Only the guest can modify this booking.")

        # редактировать только пока бронь в статусе PENDING
        if instance.status != BookingStatus.PENDING:
            raise ValidationError("Only pending bookings can be modified.")

        serializer.save()

    # ограничения для гостя при DELETE:
    def perform_destroy(self, instance):
        """Allow guest to cancel only 24 hours before checkin."""
        user = self.request.user

        # Разрешаем отмену только гостю
        if instance.guest != user:
            raise ValidationError("Only the guest can cancel this booking.")

        # datetime начала заезда: дата check_in + время 14:00 (CHECK_IN_TIME)
        check_in_dt = instance.check_in_datetime  # берём готовый datetime 14:00 из модели (@property)
        if check_in_dt is None:
            raise ValidationError("Booking has no check-in date.")

        # Приводим к текущему часовому поясу Django. Django при USE_TZ=True (в settings.py) ожидает aware datetime (с tzinfo)
        # Django уверенно понимает, сколько времени осталось до заезда, независимо от настроек сервера и БД
        check_in_dt = timezone.make_aware(check_in_dt, timezone.get_current_timezone())

        # for test:
        # now = timezone.now()
        # print("NOW:", now)
        # print("CHECK_IN_DT:", check_in_dt)
        # print("DIFF:", check_in_dt - now)

        # Если до заезда меньше суток — запрещаем отмену
        if check_in_dt - timezone.now() < timedelta(days=1):    # 24h
            raise ValidationError("Too late to cancel booking. Allow guest to cancel only 24 hours before checkin.")

        # Вместо физического удаления — помечаем как отменённую
        # видно историю, можно показывать владельцу, что бронь была, но гость её отменил.
        # отмена гостем
        instance.status = BookingStatus.CANCELLED
        instance.save(update_fields=["status"])

