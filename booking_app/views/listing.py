# booking_app/views/listing.py
from django.db.models import Q
from rest_framework import viewsets, permissions, decorators, response, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from booking_app.choices import Role
from booking_app.models import Listing
from booking_app.serializers.listing import ListingSerializer
from booking_app.permissions import IsOwnerOrReadOnly, IsOwnerUser


class ListingViewSet(viewsets.ModelViewSet):
    """
    Public listing API:
    - anyone can search and read active listings
    - owners can create and update their own listings
    """

    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]

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

    ordering_fields = ["price_per_night", "-price_per_night", "created_at", "-created_at"]
    ordering = ["-created_at"]  # Newest first

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
                self.action in ['retrieve', 'update', 'partial_update', 'destroy']
                and user.is_authenticated
                and getattr(user, "role", None) == Role.OWNER
        ):
            return Listing.objects.filter(
                Q(is_active=True) | Q(owner=user)
            ).order_by("-created_at")

        return base_qs.order_by("-created_at")

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
        """
        # Получаем конкретное объявление по pk из URL
        listing = self.get_object()

        # Переключаем статус доступности (true → false или false → true)
        listing.is_active = not listing.is_active

        # Сохраняем только изменённое поле (эффективно)
        listing.save(update_fields=["is_active"])

        # Возвращаем ID и новый статус
        return response.Response(
            {"id": listing.id, "is_active": listing.is_active},
            status=status.HTTP_200_OK,
        )

    # Кабинет хозяина:
    # GET /api/v1/listings/my/ с заголовком
    # Authorization: Token <token_хозяина>  → все его объявления, и активные, и выключенные
    @decorators.action(
        detail=False,  # /listings/my/
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated, IsOwnerUser],
        url_path="my",
    )
    def my_listings(self, request):
        """
        Return all listings owned by the current user (active and inactive).
        """
        qs = Listing.objects.filter(owner=request.user).order_by("-created_at")
        serializer = self.get_serializer(qs, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
