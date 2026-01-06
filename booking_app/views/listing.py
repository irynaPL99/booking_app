from django.db import models
from django.db.models import Q, Avg, Count
from django.db.models.functions import Coalesce # функция SQL (берёт первый не-NULL аргумент)
from django.utils import timezone
from rest_framework import viewsets, permissions, decorators, response, status
from rest_framework.decorators import action, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from booking_app.choices import Role, BookingStatus
from booking_app.models import Listing, Booking, Review
from booking_app.serializers.listing import ListingListSerializer, ListingDetailSerializer
from booking_app.permissions import IsOwnerOrReadOnly, IsOwnerUser
from booking_app.serializers.review import ReviewListSerializer


class ListingViewSet(viewsets.ModelViewSet):
    """
    Public listing API:
    - anyone can search and read active listings
    - owners can create and update their own listings
    """

    def get_serializer_class(self):
        if self.action == "list":
            return ListingListSerializer
        return ListingDetailSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    search_fields = ["title", "description"]  # Search in title OR description only

    filterset_fields = {
        "price_per_night": ["gte", "lte"],  # Price range (min/max)
        "city": ["exact", "in"],
        "region": ["exact"],  # district (Nordrhein-Westfalen, Bayern...)
        "rooms": ["gte", "lte"],  # Rooms range
        "listing_type": ["exact"],  # Property type
        "is_active": ["exact"],  # Active status
    }

    ordering_fields = [
        "price_per_night", "-price_per_night",
        "created_at", "-created_at",
        "average_rating", "-average_rating",
        "review_count", "-review_count",
    ]
    ordering = ["-average_rating", "review_count"]  # по умолчанию

    def get_queryset(self):
        """
        For list/search: only active listings for everyone.
        For retrieve:
        - guests/non-owners: only active
        - owner: active + his own listings (even inactive)
        """
        base_qs = Listing.objects.filter(is_active=True)

        user = self.request.user
        if (
                self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'toggle_active']
                and user.is_authenticated
                and getattr(user, "role", None) == Role.OWNER
        ):
            return Listing.objects.filter(
                Q(is_active=True) | Q(owner=user)
            ).annotate(
                # Результат всегда FloatField. Если null — замени на 0.0
                average_rating=Coalesce(Avg("reviews__rating"), 0.0, output_field=models.FloatField()),
                review_count=Count("reviews"),
            ).order_by("-created_at")

        return base_qs.annotate(
            average_rating=Coalesce(Avg("reviews__rating"),0.0, output_field=models.FloatField()),
            review_count=Count("reviews"),
        ).order_by("-created_at")

    def get_permissions(self):
        """
        Allow anyone to read listings.
        For create/update/delete require authenticated user and listing owner.
        """
        # авторизованные могут менять только свои объекты (через IsOwnerOrReadOnly)
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerUser, IsOwnerOrReadOnly]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """
        Save a new listing with the current user set as the owner.
        """
        # автоматически подставляем owner=self.request.user,
        # так что клиенту не нужно передавать owner в JSON, и нельзя украсть чужой объект
        serializer.save(owner=self.request.user)

    # Эндпоинт: POST / api/v1/listings/{id}/toggle-active/ - включить/выключить доступность (is_active), (только владелец)
    # Результат: {"id": 1, "is_active": false} — переключает доступность объявления.
    # @action — это декоратор, который добавляет  кастомные эндпоинты к ViewSet помимо
    # стандартных  CRUD(list, create, retrieve, update, destroy).
    @decorators.action(
        detail=True,            # true = /listings/{pk}/toggle-active/
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly], # только владелец
        url_path="toggle-active",
    )
    def toggle_active(self, request, pk=None):
        """
        Switch listing availability on or off by toggling the is_active flag.

        When deactivating a listing, automatically reject all pending future
        bookings for this listing, but keep confirmed bookings unchanged.
        """
        # Получаем конкретное объявление по pk из URL
        listing = self.get_object()

        # можно явно перепроверить
        if listing.owner != request.user:
            return response.Response(
                {"detail": "Only listing owner can change availability."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Переключаем статус доступности (true → false или false → true)
        listing.is_active = not listing.is_active
        # Сохраняем только изменённое поле (эффективно)
        listing.save(update_fields=["is_active"])

        # автоотклоненные брони
        auto_rejected = 0

        # Если объявление выключили — обработать pending-брони
        if not listing.is_active:
            today = timezone.now().date()

            pending_qs = Booking.objects.filter(
                listing=listing,
                status=BookingStatus.PENDING,
                check_in__gt=today,  # только будущие заезды
            )
            auto_rejected = pending_qs.update(status=BookingStatus.REJECTED)
            message = (
                "Listing deactivated. All pending future bookings were rejected. "
                "Confirmed future bookings must be cancelled manually by the owner "
                "or honoured."
            )
        else:
            message = "Listing activated."

        return response.Response(
            {
                "id": listing.id,
                "is_active": listing.is_active,
                "auto_rejected_bookings": auto_rejected,    # кол-во
                "detail": message,
            },
            status=status.HTTP_200_OK,
        )

    # Кабинет хозяина:
    # GET /api/v1/listings/my/ с токеном
    # Authorization: Token <token_хозяина>  → все его объявления, и активные, и выключенные
    @decorators.action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated, IsOwnerUser],
        url_path="my",
    )
    def my_listings(self, request):
        """
        Return all listings owned by the current user (active and inactive).
        """
        qs = Listing.objects.filter(owner=request.user).annotate(
            # Coalesce (null -> 0)
            average_rating=Coalesce(Avg("reviews__rating"), 0.0, output_field=models.FloatField()),
            review_count=Count("reviews"),
        ).order_by("-created_at")

        serializer = self.get_serializer(qs, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


    @decorators.action(
        detail=True,  # true = /listings/{pk}/reviews/
        methods=["get"],
        url_path="reviews",
    )
    @permission_classes([permissions.IsAuthenticated])
    def reviews(self, request, pk=None):
        """
        Only for authenticated users.
        Return all reviews for this listing(id).
        Only for active listings (or owner's own inactive listings).
        """
        listing = self.get_object()  # Получаем listing (применяется логика get_queryset) с проверкой прав/активности
        # авторизованные увидят активные + свои неактивные
        qs = Review.objects.filter(listing=listing) \
            .select_related('author') \
            .order_by("-created_at")
        serializer = ReviewListSerializer(qs, many=True)
        return response.Response(serializer.data)