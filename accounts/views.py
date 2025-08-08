from django.conf import settings
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.views import APIView
# from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from .utils import get_tokens_for_user
from .serializers import UserSerializer, RegisterSerializer
from bamina.utils.response import Response
from bamina.config.env import env


class UserDetailView(APIView):
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(data=serializer.data, message="User fetched successfully")


user_detail_view = UserDetailView.as_view()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                success=False,
                message="Validation failed",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()
        stay_logged_in = str(request.data.get(
            "stay_logged_in", False)).lower() == "true"

        tokens = get_tokens_for_user(user, stay_logged_in)

        response = Response(
            {
                "access": tokens['access'],
            },
            message="User registered successfully.",
            status=status.HTTP_201_CREATED
        )

        response.set_cookie(
            key='refresh_token',
            value=tokens['refresh'],
            httponly=True,
            secure=True,
            samesite='None',
            max_age=7 * 24 * 60 * 60 if stay_logged_in else 24 * 60 * 60,
        )

        return response


register_user_view = RegisterView.as_view()


User = get_user_model()


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                success=False,
                message="Failed to send email",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)

        FRONTEND_BASE_URL = env('FRONTEND_BASE_URL')

        reset_link = f"{FRONTEND_BASE_URL}/reset-password?uidb64={uidb64}&token={token}"

        # send_mail(
        #     subject="Reset your password",
        #     message=f"Click the link to reset your password: {reset_link}",
        #     from_email=None,
        #     recipient_list=[user.email],
        # )

        subject = "Reset Your Password – Bamina Online Shopping Store"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email

        html_content = render_to_string("emails/password_reset_email.html", {
            "user_name": user.full_name or user.email,
            "reset_link": reset_link,
            "current_year": now().year,
        })

        email = EmailMultiAlternatives(subject, "", from_email, [to_email])
        email.attach_alternative(html_content, "text/html")
        email.send()

        return Response({"message": "Password reset link sent."}, status=status.HTTP_200_OK)


password_reset_request_view = PasswordResetRequestView.as_view()


class PasswordResetConfirmView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                success=False,
                message="Failed to confirm password",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)


password_reset_confirm_view = PasswordResetConfirmView.as_view()
