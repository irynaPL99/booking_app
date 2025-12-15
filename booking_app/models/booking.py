from datetime import datetime, time
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import AbstractBaseModel
from .listing import Listing
from booking_app.choices import BookingStatus


class Booking(AbstractBaseModel):
    """
    Booking model that stores reservation details for a listing.
    """

    CHECK_IN_TIME = time(14, 0)
    CHECK_OUT_TIME = time(12, 0)

    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name=_("Guest"),
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name=_("Listing"),
    )
    check_in = models.DateField(
        _("Check-in date"),
    )
    check_out = models.DateField(
        _("Check-out date"),
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
    )
    guests_count = models.PositiveIntegerField(
        _("Guests count"),
        default=1,
    )

    @property
    def check_in_datetime(self):
        """
        Return full check-in datetime with default time 14:00.
        """
        if not self.check_in:
            return None
        return datetime.combine(self.check_in, self.CHECK_IN_TIME)

    @property
    def check_out_datetime(self):
        """
        Return full check-out datetime with default time 12:00.
        """
        if not self.check_out:
            return None
        return datetime.combine(self.check_out, self.CHECK_OUT_TIME)

    @property
    def nights(self) -> int:
        """
        Calculate number of nights between check-in and check-out.
        """
        if not self.check_in or not self.check_out:
            return 0
        delta = self.check_out - self.check_in
        return max(delta.days, 0)

    @property
    def total_price(self) -> Decimal:
        """
        Calculate total price for the stay based on listing price per night.
        """
        if not self.listing or self.listing.price_per_night is None:
            return Decimal("0.00")
        return Decimal(self.nights) * self.listing.price_per_night

    def clean(self):
        """
        Validate booking business rules (min 1 night, dates order, etc.).
        """
        super().clean()     # ← Вызывает AbstractBaseModel.clean() (пустой),  "выполни валидацию родителей перед моей"

        if self.check_in and self.check_out and self.check_out <= self.check_in:
            raise ValidationError(_("Check-out date must be after check-in date."))

        if self.nights < 1:
            raise ValidationError(_("Minimum stay is 1 night."))

    def save(self, *args, **kwargs):
        """
        Ensure model is validated before saving.
        """
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.listing} | {self.guest} | {self.check_in} - {self.check_out}"
