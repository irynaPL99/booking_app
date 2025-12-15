from rest_framework.routers import DefaultRouter

from booking_app.views.listing import ListingViewSet

router = DefaultRouter()
router.register("", ListingViewSet, basename="listing")

urlpatterns = router.urls
