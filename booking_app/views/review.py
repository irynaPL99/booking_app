from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError

from booking_app.models import Review
from booking_app.serializers.review import ReviewCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Allow authenticated users to create reviews for listings
    they have stayed at. One review per listing per author.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        # защита от второго отзыва на тот же listing
        listing = serializer.validated_data.get("listing")
        if Review.objects.filter(listing=listing, author=user).exists():
            raise ValidationError(
                {"detail": "You have already left a review for this listing."}
            )

        serializer.save(author=user)

    def perform_update(self, serializer):
        """Allow only the author to edit their review."""
        instance = self.get_object()
        user = self.request.user

        if instance.author != user:
            raise ValidationError("Only the author can modify this review.")

        serializer.save()

    def perform_destroy(self, instance):
        """Allow deleting only by author or admin."""
        user = self.request.user

        if instance.author != user and not user.is_staff:
            raise ValidationError("Only the author or an admin can delete this review.")

        instance.delete()
