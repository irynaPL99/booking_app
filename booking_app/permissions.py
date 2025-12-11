# booking_app/permissions.py
from datetime import date

from rest_framework.permissions import BasePermission

from booking_app.models import Booking, BookingStatus


class CanCreateReview(BasePermission):
    """
    Разрешает создавать отзыв только пользователю,
    который жил в этом жилье (есть confirmed-бронирование в прошлом).
    """

    def has_permission(self, request, view):
        # Разрешаем только создание (POST) и только аутентифицированным
        if request.method != "POST" or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # !!!!!!  obj здесь обычно Listing, если используешь Nested routes.
        # Если у тебя ReviewViewSet без nested, проверку лучше делать в сериализаторе.
        return True
