# views/booking.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from booking_app.models import Booking
from booking_app.permissions import IsOwnerUser
from booking_app.serializers.booking import BookingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    """API for guest bookings. Only own bookings visible."""

    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def get_queryset(self):
        """Return only authenticated user's bookings."""
        return Booking.objects.filter(guest=self.request.user)

    def perform_create(self, serializer):
        """Set current user as booking guest."""
        serializer.save(guest=self.request.user)

    # GET /bookings/owner_bookings/
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsOwnerUser])
    def owner_bookings(self, request):
        """List bookings for owner's listings."""
        qs = Booking.objects.filter(listing__owner=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
