from rest_framework.routers import DefaultRouter
from booking_app.views.review import ReviewViewSet

router = DefaultRouter()

# /api/v1/reviews/...(/reviews/{id}/, /reviews/my/, /reviews/owner/)
router.register("", ReviewViewSet, basename="review")


urlpatterns = router.urls