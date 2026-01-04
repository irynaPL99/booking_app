from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()  # берём кастомную модель из AUTH_USER_MODEL(settings.py)


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    # Password comes only from request and is not returned in response
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'role']
        extra_kwargs = {
            # If role is not sent, default value (CUSTOMER) from the model is used
            "role": {"required": False},
        }

    def create(self, validated_data):
        # Use create_user so Django hashes the password correctly
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile update."""

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id', 'email', 'role']