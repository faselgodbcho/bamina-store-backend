from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password as validate_user_password

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'profile_photo']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password']

    def validate_password(self, value):
        validate_user_password(value)
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return value

    def create(self, validated_data):
        try:
            user = User.objects.create_user(
                full_name=validated_data['full_name'],
                email=validated_data['email'],
                password=validated_data['password']
            )
            return user
        except IntegrityError:
            raise serializers.ValidationError(
                {"email": "A user with this email already exists."})


User = get_user_model()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No user is associated with this email.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data["uidb64"]))
            user = User.objects.get(pk=uid)
        except Exception:
            raise serializers.ValidationError("Invalid token or user ID.")

        token = data['token']
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Invalid or expired token.")

        self.context["user"] = user
        return data

    def save(self):
        user = self.context["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()
