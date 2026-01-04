from django.urls import path, include

urlpatterns = [
    path("listings/", include("booking_app.urls.listing")),
    path("bookings/", include("booking_app.urls.booking")),
    path("reviews/", include("booking_app.urls.review")),
    path("users/", include("booking_app.urls.user")),
    path("auth/", include("booking_app.urls.auth")),

]