from rest_framework.routers import DefaultRouter

from booking_app.views.review import ReviewViewSet

router = DefaultRouter()
router.register("", ReviewViewSet, basename="review")

urlpatterns = router.urls