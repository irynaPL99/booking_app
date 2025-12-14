# booking_app/urls/listing.py

from rest_framework.routers import DefaultRouter

from booking_app.views.listing import ListingViewSet

router = DefaultRouter()
router.register("listings", ListingViewSet, basename="listing")

urlpatterns = router.urls
