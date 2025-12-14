# booking_app/choices.py
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    CUSTOMER = "customer", _("Customer")
    OWNER = "owner", _("Owner")
    # "customer" — это value, которое хранится в БД и передаётся в запросах
    # _("Customer") — это label, человекочитаемое название, которое Django сам воспринимает как label
    # Django собирает все строки внутри _() в .po файлы (django-admin makemessages)
    # для поддержки перевода интерфейса (i18n)


class ListingType(models.TextChoices):
    APARTMENT = "apartment", _("Apartment")
    ROOM = "room", _("Room")
    HOUSE = "house", _("House")


class BookingStatus(models.TextChoices):
    PENDING = "pending", _("Pending")        # запрос отправлен, ждёт решения владельца
    CONFIRMED = "confirmed", _("Confirmed")  # владелец подтвердил бронь
    REJECTED = "rejected", _("Rejected")    # владелец отклонил
    CANCELLED = "cancelled", _("Cancelled")  # гость отменил бронь
