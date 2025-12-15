from django.urls import path
from booking_app.views.auth import (
    RegisterView, TokenLoginView, LogoutView, ChangePasswordView, )

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", TokenLoginView.as_view(), name="token-login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]
