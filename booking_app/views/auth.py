# views/auth.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from booking_app.serializers.user import RegisterSerializer
from booking_app.serializers.auth_token import TokenLoginSerializer
from booking_app.serializers.change_password import ChangePasswordSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Simple API endpoint to create a new user account.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []  # Anyone can call this endpoint (no login required)


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

class LogoutView(APIView):
     """Logout user by deleting auth token."""
     permission_classes = [permissions.IsAuthenticated]

     def post(self, request):
         Token.objects.filter(user=request.user).delete()
         return Response({"message": "Logged out"}, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    """Allow authenticated user to change own password."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Validate old/new password and update user password."""
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        new_password = serializer.validated_data["new_password"]
        user.set_password(new_password)
        user.save()

        # сбросить старый токен и выдать новый
        # «получи токен для этого пользователя,
        # а если его еще нет — создай, и верни объект токена, а флаг created - не нужен»
        Token.objects.filter(user=user).delete()
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {"message": "Password changed successfully", "token": token.key},
            status=status.HTTP_200_OK,
        )