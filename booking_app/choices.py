# booking_app/choices.py
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    CUSTOMER = "customer", _("Customer")
    OWNER = "owner", _("Owner")


class ListingType(models.TextChoices):
    APARTMENT = "apartment", _("Apartment")
    ROOM = "room", _("Room")
    HOUSE = "house", _("House")


class BookingStatus(models.TextChoices):
    PENDING = "pending", _("Pending")        # запрос отправлен, ждёт решения владельца
    CONFIRMED = "confirmed", _("Confirmed")  # владелец подтвердил бронь
    REJECTED = "rejected", _("Rejected")    # владелец отклонил
    CANCELLED = "cancelled", _("Cancelled")  # гость отменил бронь
