from rest_framework.routers import DefaultRouter

from booking_app.views.listing import ListingViewSet

router = DefaultRouter()
# CRUD +  listings/(?P<listing_pk>\d+)/reviews
router.register("", ListingViewSet, basename="listing")

urlpatterns = router.urls
