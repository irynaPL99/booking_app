from django.contrib import admin
from django.db import models
from django.db.models import Count, Avg
from django.db.models.functions import Coalesce
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
    Displays owner, full address, city, type, average_rating, review_count, active status.
    """

    list_display = (
        "id",
        "full_address",
        "city",
        "listing_type",
        "owner",
        "average_rating",
        "review_count",
        "is_active",
    )
    list_filter = ("city", "is_active", "listing_type")
    search_fields = ['title', 'description', 'city']
    readonly_fields = ['average_rating', 'review_count']

    def full_address(self, obj):
        """
        Show full address using Listing property.
        """
        return obj.full_address     # @property for class Listing(AbstractBaseModel)

    full_address.short_description = "Full address"

    # Без него: админка покажет только поля модели → нет average_rating
    def get_queryset(self, request):
        """
        Add rating and review count to all listings.
        Runs one SQL query with JOINs.
        """

        return super().get_queryset(request).annotate(
            average_rating=Coalesce(Avg("reviews__rating"), 0.0, output_field=models.FloatField()),
            review_count=Count("reviews")
        )

    def average_rating(self, obj):
        """
        Show rating with 1 decimal place. 0.0 if no reviews.
        """
        return f"{obj.average_rating:.1f}" if obj.average_rating else "0.0"

    average_rating.short_description = "Rating"
    average_rating.admin_order_field = "average_rating"

    def review_count(self, obj):
        """
        Show total number of reviews for this listing.
        """
        return obj.review_count

    review_count.short_description = "Reviews"
    review_count.admin_order_field = "review_count"



@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Admin configuration for bookings.
    Prevents owners from booking their own listings.
    """

    list_display = (
        "id",
        "listing_id_col",  # ID объявления
        "listing_full_address",
        "guest",
        "status",
        "check_in",
        "check_out",
        "total_price",
    )
    list_filter = ("status",)

    def listing_id_col(self, obj):
        """
        Show listing ID number in admin table column.
        """
        return obj.listing_id  # это FK_id, Django создаёт автоматически

    listing_id_col.short_description = "Listing ID"

    def listing_full_address(self, obj):
        """
        Show full address of the related listing.
        """
        if not obj.listing:
            return "-"
        return obj.listing.full_address  # property вместо utils

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
        "id",
        "listing_id_col",  # ID объявления
        "listing_full_address",
        "listing_type",
        "author",
        "rating",
        "created_at",
        "updated_at",
        "comment_preview",
    )
    list_filter = ["rating", "created_at", "updated_at"]
    search_fields = ["comment"]

    def listing_id_col(self, obj):
        """
        Show listing ID number in admin table column.
        """
        return obj.listing_id  # это FK_id, Django создаёт автоматически

    listing_id_col.short_description = "Listing ID"

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

    def comment_preview(self, obj):
        """
        Show readable listing type.
        """
        return obj.comment[:20] + "..." if obj.comment else "-"

    comment_preview.short_description = "Comment"
