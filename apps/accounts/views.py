from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView


from apps.core.exceptions import DomainError

from . import services
from .serializers import (
    LoginSerializer,
    MeSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
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
        return Response({"detail": "کد تأیید شد.", **tokens_for_user(user)}, status=status.HTTP_200_OK)


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
        return Response(tokens_for_user(user), status=status.HTTP_200_OK)


class MeView(generics.RetrieveUpdateAPIView):


    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user



