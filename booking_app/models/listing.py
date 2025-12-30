from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import AbstractBaseModel
from booking_app.choices import ListingType


class Listing(AbstractBaseModel):
    """
    Listing model that stores rental property information.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
        verbose_name=_("Owner"),
    )
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), blank=True, null=True)

    region = models.CharField(
        _("Region"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Federal state or region in Germany (e.g. Bavaria, NRW)."),
    )

    city = models.CharField(_("City"), max_length=100)
    postal_code = models.CharField(_("Postal code"), max_length=10)
    street = models.CharField(_("Street"), max_length=255)
    house_number = models.CharField(_("House number"), max_length=20)
    house_suffix = models.CharField(
        _("House suffix"),
        max_length=20,
        blank=True,
        help_text=_("Addition to the house number (e.g. A, B, courtyard apartment, app 12, etc.)."),
    )

    price_per_night = models.DecimalField(
        _("Price per night"),
        max_digits=10,
        decimal_places=2,
    )
    max_guests = models.PositiveIntegerField(
        _("Max guests"),
    )
    listing_type = models.CharField(
        _("Listing type"),
        max_length=20,
        choices=ListingType.choices,
        default=ListingType.APARTMENT,
    )
    rooms = models.PositiveIntegerField(_("Rooms"), default=1)

    # статус объявления (активно/неактивно) для «управления доступностью»
    is_active = models.BooleanField(
        _("Is active"),
        default=True,
    )

    @property
    def full_address(self) -> str:
        """
        Return human-readable full address for this listing.
        """
        parts = [self.street, self.house_number]
        if self.house_suffix:
            parts.append(self.house_suffix)
        parts.extend([self.postal_code, self.city])
        return " ".join(str(p) for p in parts if p)

    class Meta:
        verbose_name = _("Listing")
        verbose_name_plural = _("Listings")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "street",
                    "house_number",
                    "house_suffix",
                    "postal_code",
                    "city",
                    "listing_type",
                ],
                name="unique_property_by_address",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.city})"
