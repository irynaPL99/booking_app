from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from booking_app.serializers.user import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """User profile management (current user only)."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return current authenticated user."""
        return self.request.user


    # везде + Authorization: Token <твой_токен>:
    # GET /api/v1/users/me/ — посмотреть себя
    # PATCH /api/v1/users/me/ — обновить свои поля
    # DELETE /api/v1/users/me/ — удалить учетку
    @action(detail=False, methods=["get", "patch", "delete"])
    def me(self, request):
        """Get, update or delete current user account."""
        user = request.user

        if request.method.lower() == "get":
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        if request.method.lower() == "patch":
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        if request.method.lower() == "delete":
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
