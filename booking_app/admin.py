from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User, Listing, Booking, Review



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Admin configuration for the custom User model.
    Shows basic identity and role information.
    """

    list_display = ("email", "first_name", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_active")


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """
    Admin configuration for property listings.
    Displays owner, full address, city, type and active status.
    """

    list_display = (
        "full_address",
        "city",
        "listing_type",
        "owner",
        "is_active",
    )
    list_filter = ("city", "is_active", "listing_type")

    def full_address(self, obj):
        """
        Show full address using Listing property.
        """
        return obj.full_address     # @property for class Listing(AbstractBaseModel)

    full_address.short_description = "Full address"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Admin configuration for bookings.
    Prevents owners from booking their own listings.
    """

    list_display = (
        "listing_full_address",
        "guest",
        "status",
        "check_in",
        "check_out",
        "total_price",
    )
    list_filter = ("status",)

    def listing_full_address(self, obj):
        """
        Show full address of the related listing.
        """
        if not obj.listing:
            return "-"
        return obj.listing.full_address  # используем property вместо utils

    listing_full_address.short_description = "Listing address"

    def save_model(self, request, obj, form, change):
        """
        Validate that owner cannot book their own listing.
        """
        if obj.listing and obj.guest and obj.listing.owner == obj.guest:
            raise ValidationError(_("Owner cannot book their own listing."))
        super().save_model(request, obj, form, change)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin configuration for reviews with listing details.
    """

    list_display = (
        "listing_full_address",
        "listing_type",
        "author",
        "rating",
        "created_at",
    )
    list_filter = ("rating",)

    def listing_full_address(self, obj):
        """
        Show full address of the related listing.
        """
        if not obj.listing:
            return "-"
        return obj.listing.full_address     # @property for class Listing(AbstractBaseModel)

    listing_full_address.short_description = "Listing address"

    def listing_type(self, obj):
        """
        Show readable listing type.
        """
        if not obj.listing:
            return "-"
        return obj.listing.get_listing_type_display()

    listing_type.short_description = "Type"
