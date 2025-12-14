# booking_app/urls/booking.py

from rest_framework.routers import DefaultRouter

from booking_app.views.booking import BookingViewSet

router = DefaultRouter()
router.register("bookings", BookingViewSet, basename="booking")

urlpatterns = router.urls