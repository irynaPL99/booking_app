# booking_app/serializers/review.py
from datetime import date

from rest_framework import serializers

from booking_app.models import Review, Booking, BookingStatus


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "listing", "rating", "comment")

    def validate(self, attrs):
        user = self.context["request"].user
        listing = attrs["listing"]
        today = date.today()

        # Есть ли хотя бы одно подтверждённое бронирование в прошлом
        has_stayed = Booking.objects.filter(
            guest=user,
            listing=listing,
            status=BookingStatus.CONFIRMED,
            check_out__lt=today,
        ).exists()

        if not has_stayed:
            raise serializers.ValidationError(
                "You can leave a review only after a confirmed booking has been completed."
            )

        return attrs
