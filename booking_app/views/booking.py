from django.utils import timezone
from datetime import timedelta

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from booking_app.choices import Role
from booking_app.models import Booking
from booking_app.serializers.booking import BookingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    """API for guest bookings. Only own bookings visible."""

    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def get_queryset(self):
        """Return only authenticated user's bookings."""
        return Booking.objects.filter(guest=self.request.user) # customer видит только свои брони

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

        qs = Booking.objects.filter(listing__owner=user).order_by("-checkin")
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
        """Allow owner to confirm or cancel a booking."""
        booking = self.get_object()
        user = request.user

        # Только хозяин объявления может менять статус
        if booking.listing.owner != user:
            return Response(
                {"detail": "Only listing owner can change booking status."},
                status=status.HTTP_403_FORBIDDEN,
            )

        new_status = request.data.get("status")
        if new_status not in ["confirmed", "cancelled"]:
            return Response(
                {"detail": "Invalid status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = new_status
        booking.save(update_fields=["status"])

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    # ограничения для гостя при DELETE:
    def perform_destroy(self, instance):
        """Allow guest to cancel only 1 day before checkin."""
        user = self.request.user
        if instance.guest == user:
            if instance.checkin - timezone.now().date() < timedelta(days=1):
                raise ValidationError("Too late to cancel booking.")
        instance.delete()