# views/auth.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from booking_app.serializers.user import RegisterSerializer
from booking_app.serializers.auth import LoginSerializer
from booking_app.serializers.auth_token import TokenLoginSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Simple API endpoint to create a new user account.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []  # Anyone can call this endpoint (no login required)

class LoginView(APIView):
    """
    Simple login endpoint. It only checks email and password.
    """
    permission_classes = []  # open for anyone

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        #  вернуть info о пользователе
        return Response(
            {
                "message": "Login successful",
                "email": user.email,
                "first_name": user.first_name,
                "role": user.role,
            },
            status=status.HTTP_200_OK,
        )

class TokenLoginView(APIView):
    """
    Login with email and password and return auth token.
    """
    permission_classes = []  # open for anyone

    def post(self, request):
        serializer = TokenLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        return Response({"token": token.key}, status=status.HTTP_200_OK)