from rest_framework import serializers
from booking_app.models import Booking, Listing


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for booking creation and listing."""

    listing = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.filter(is_active=True)
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'check_in', 'check_out',
            'guests_count', 'status', 'total_price'
        ]
        read_only_fields = ['guest', 'status', 'total_price']


