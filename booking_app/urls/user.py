from rest_framework.routers import DefaultRouter

from booking_app.views.user import UserViewSet

router = DefaultRouter()
router.register("", UserViewSet, basename="user")

urlpatterns = router.urls