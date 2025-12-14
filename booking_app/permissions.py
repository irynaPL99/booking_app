# booking_app/permissions.py

from datetime import date

from rest_framework import permissions
from rest_framework.permissions import BasePermission

from booking_app.choices import Role
from booking_app.models import Booking, BookingStatus

class IsOwnerUser(permissions.BasePermission):
    """
    Allow access only to users with role=owner.
    """
    # срабатывает на уровне всего запроса, ещё до того, как DRF достаёт конкретный объект
    # «Это залогиненный пользователь с ролью owner или нет?»
    # Подходит: «Создавать объявления могут только пользователи с ролью owner».
    # «Этот endpoint вообще доступен только владельцам (арендодателям)».
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == Role.OWNER
        )

class IsCustomerUser(permissions.BasePermission):
    """
    Allow access only to users with role=customer.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == Role.CUSTOMER
        )

class CanCreateReview(BasePermission):
    """
    Allow creating a review only for a user
    who has a confirmed past booking for this listing.
    """

    def has_permission(self, request, view):
        """
        Allow only POST and only authenticated users.
        """
        if request.method != "POST":
            return False
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        """
        Here `obj` would usually be a Listing if using nested routes.
        If you use a flat ReviewViewSet, better do this check in the serializer.
        """
        # Placeholder: always allow for now
        # Пока заглушка — полная проверка «была ли бронь» делается в ReviewSerializer.validate().
        return True


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow read for anyone, write only for object owner.
    """
    # Проверяет уже конкретный объект (listing, booking и т.д.).
    # Любой может смотреть объявление, но редактировать/удалять может только тот пользователь,
    # который записан в поле owner у этого объявления
    # Без IsOwnerOrReadOnly владелец по роли мог бы редактировать чужие объекты, если как‑то до них доберётся по ID.

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  # GET/HEAD/OPTIONS
            return True                                 # любой смотрит
        return getattr(obj, "owner", None) == request.user  # редактировать — только хозяин
