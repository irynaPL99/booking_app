from datetime import date

from rest_framework import serializers

from booking_app.models import Review, Booking, BookingStatus


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "listing", "rating", "comment", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        user = self.context["request"].user
        listing = attrs.get("listing") # ! get лучше. т.к. получу None если листинг не придет
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
                {"comment" : "You can leave a review only after a confirmed booking has been completed." }
            )

        return attrs


class ReviewListSerializer(serializers.ModelSerializer):
    """Reviews for listing detail page."""
    #author_name = serializers.ReadOnlyField(source='author.first_name')
    # get_full_name() возвращает "First Name Last Name", а если оба пустые — возвращает username.
    author_name = serializers.ReadOnlyField(source='author.get_full_name')
    listing_title = serializers.ReadOnlyField(source='listing.title')

    class Meta:
        model = Review
        fields = ['id', 'author_name', 'rating', 'comment', 'created_at', 'updated_at', 'listing_title']
        read_only_fields = fields