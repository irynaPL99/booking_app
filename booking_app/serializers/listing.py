from rest_framework import serializers

from booking_app.models import Listing


class ListingListSerializer(serializers.ModelSerializer):
    """Short listing data for list endpoints."""

    class Meta:
        model = Listing
        fields = [
            "id",
            "title",
            "city",
            "price_per_night",
            "rooms",
            "is_active",
        ]


class ListingDetailSerializer(serializers.ModelSerializer):
    """Full listing data for detail endpoints."""

    owner = serializers.ReadOnlyField(source="owner.email")
    full_address = serializers.ReadOnlyField()

    class Meta:
        model = Listing
        fields = "__all__"
        read_only_fields = [
            "id",
            "owner",
            "full_address",
            "created_at",
            "updated_at",
        ]
