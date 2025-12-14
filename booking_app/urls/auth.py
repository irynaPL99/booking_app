from django.urls import path
from booking_app.views.auth import RegisterView, LoginView, TokenLoginView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    #path("auth/login/", LoginView.as_view(), name="login"), # old
    path("auth/token/", TokenLoginView.as_view(), name="token-login"),
]
