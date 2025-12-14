#  booking_app/serializers/listing.py

from rest_framework import serializers

from booking_app.models import Listing


class ListingSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.email")
    full_address = serializers.ReadOnlyField()

    class Meta:
        model = Listing
        fields = [
            "id",
            "owner",
            "title",
            "description",
            "region",
            "city",
            "postal_code",
            "street",
            "house_number",
            "house_suffix",
            "full_address",         # @property, собирает строку из частей адреса
            "price_per_night",
            "max_guests",
            "listing_type",
            "rooms",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "full_address", "created_at", "updated_at"]
