from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from apps.core.exceptions import DomainError

from . import services
from .authentication import (
    REFRESH_TOKEN_COOKIE,
    clear_auth_cookies,
    enforce_csrf,
    set_auth_cookies,
)
from .serializers import (
    LoginSerializer,
    MeSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    PasswordResetSerializer,
    RegisterSerializer,
    tokens_for_user,
)
from .tasks import send_otp_email, send_otp_sms

User = get_user_model()


def _client_ip(request) -> str | None:
    return request.META.get("REMOTE_ADDR")


class RegisterView(generics.CreateAPIView):


    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class OTPRequestView(APIView):


    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp"

    @extend_schema(request=OTPRequestSerializer, responses={202: None})
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data["identifier"]
        purpose = serializer.validated_data["purpose"]

        services.ensure_otp_rate_limit(identifier)
        code = services.generate_otp(identifier, purpose, ip=_client_ip(request))
        if "@" in identifier:
            send_otp_email.delay(identifier, code)
        else:
            send_otp_sms.delay(identifier, code)
        return Response({"detail": "کد ارسال شد."}, status=status.HTTP_202_ACCEPTED)


class OTPVerifyView(APIView):


    permission_classes = [permissions.AllowAny]

    @extend_schema(request=OTPVerifySerializer)
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data["identifier"]
        purpose = serializer.validated_data["purpose"]
        code = serializer.validated_data["code"]

        try:
            services.verify_otp(identifier, purpose, code)
        except DomainError:
            raise

        user = User.objects.filter(email__iexact=identifier).first() or User.objects.filter(
            phone=identifier
        ).first()
        if user is None:
            return Response({"detail": "کد تأیید شد."}, status=status.HTTP_200_OK)

        user.is_verified = True
        user.save(update_fields=["is_verified"])
        response = Response({"detail": "کد تأیید شد."}, status=status.HTTP_200_OK)
        set_auth_cookies(response, tokens_for_user(user), request)
        return response


class PasswordResetView(APIView):
    """Reset a user's password after successful reset-purpose OTP verification."""

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=PasswordResetSerializer,
        responses={200: OpenApiResponse(description="Password reset successful")},
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"]
        code = serializer.validated_data["code"]
        new_password = serializer.validated_data["new_password"]

        services.verify_otp(identifier, "reset", code)

        user = User.objects.filter(email__iexact=identifier).first()
        if user is None:
            user = User.objects.filter(phone=identifier).first()

        if user is None:
            return Response(
                {"detail": "درخواست بازیابی معتبر نیست."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response(
            {"detail": "رمز عبور با موفقیت تغییر کرد."},
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):


    permission_classes = [permissions.AllowAny]

    @extend_schema(request=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            raise DomainError("نام کاربری یا رمز عبور نادرست است.", code="invalid_credentials", status_code=401)
        response = Response({"detail": "ورود موفق بود."}, status=status.HTTP_200_OK)
        set_auth_cookies(response, tokens_for_user(user), request)
        return response


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    throttle_classes = [ScopedRateThrottle]
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_scope = "google_login"

    def get_response(self):
        response = Response({"detail": "ورود با گوگل موفق بود."}, status=status.HTTP_200_OK)
        set_auth_cookies(response, tokens_for_user(self.user), self.request)
        return response


class CookieTokenRefreshView(TokenRefreshView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(REFRESH_TOKEN_COOKIE)
        if refresh_token is None:
            return Response({"detail": "Refresh token cookie is missing."}, status=status.HTTP_401_UNAUTHORIZED)

        enforce_csrf(request)
        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response({"detail": "Refresh token is invalid or revoked."}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response({"detail": "Token refreshed."}, status=status.HTTP_200_OK)
        set_auth_cookies(response, serializer.validated_data, request)
        return response


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        enforce_csrf(request)
        refresh_token = request.COOKIES.get(REFRESH_TOKEN_COOKIE)
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass

        response = Response({"detail": "خروج موفق بود."}, status=status.HTTP_200_OK)
        clear_auth_cookies(response)
        return response


class MeView(generics.RetrieveUpdateAPIView):


    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user



