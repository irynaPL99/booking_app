from rest_framework import serializers

from booking_app.models import Listing


class ListingListSerializer(serializers.ModelSerializer):
    """Short listing data for list endpoints."""
    #  брать поле average_rating с объекта (Имя поля = имя аннотации)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()

    class Meta:
        model = Listing
        fields = [
            "id",
            "title",
            "city",
            "price_per_night",
            "rooms",
            "is_active",
            "average_rating",
            "review_count",
        ]

class ListingDetailSerializer(serializers.ModelSerializer):
    """Full listing data for detail endpoints."""
    #  брать поле email с объекта (Имя поля ≠ имя атрибута)
    owner = serializers.ReadOnlyField(source="owner.email")
    full_address = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()

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
