from rest_framework import viewsets, permissions, response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from booking_app.models import Review, Listing
from booking_app.serializers.review import ReviewCreateSerializer, ReviewListSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ Allow authenticated users to create reviews for listings
    they have stayed at. One review per listing per author. """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Use list serializer for read, create serializer for write."""
        if self.action in ['list', 'retrieve', 'my', 'owner']:
            return ReviewListSerializer
        return ReviewCreateSerializer

    def get_queryset(self):
        """
        Base queryset for /reviews/ and nested /listings/{listing_pk}/reviews/.
        If listing_pk is in URL, return reviews for that listing only.
        """
        qs = Review.objects.all().select_related('listing', 'author')

        listing_pk = self.kwargs.get("listing_pk")
        if listing_pk is not None:
            # /api/v1/listings/{listing_pk}/reviews/
            listing = get_object_or_404(Listing, pk=listing_pk, is_active=True)
            return qs.filter(listing=listing).order_by("-created_at")

        # /api/v1/reviews/ – all reviews
        return qs.order_by("-created_at")

    @action(detail=False, methods=["get"])
    def my(self, request):
        """
        GET /api/v1/reviews/my/ - reviews written by current user.
        """
        qs = Review.objects.filter(author=request.user).select_related("listing").order_by("-created_at")
        serializer = self.get_serializer(qs, many=True)
        return response.Response(serializer.data)

    @action(detail=False, methods=["get"])
    def owner(self, request):
        """
        GET /api/v1/reviews/owner/ - all reviews for listings owned by current user.
        """
        qs = Review.objects.filter(
            listing__owner=request.user
        ).select_related("listing", "author").order_by("-created_at")
        serializer = self.get_serializer(qs, many=True)
        return response.Response(serializer.data)

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
