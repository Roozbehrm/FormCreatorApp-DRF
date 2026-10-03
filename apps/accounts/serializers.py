from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.exceptions import DomainError

from .models import OTPPurpose

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)

    class Meta:
        model = User
        fields = ("username", "email", "phone", "password")

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("این ایمیل قبلاً ثبت شده است.")
        return value

    def validate_phone(self, value):
        value = value.strip()
        if value and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("این شماره قبلاً ثبت شده است.")
        return value or None

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data, is_verified=False)
        user.set_password(password)
        user.save()
        return user


class OTPRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=64)
    purpose = serializers.ChoiceField(choices=OTPPurpose.choices)

    def validate_identifier(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("شناسه الزامی است.")
        return value.lower() if "@" in value else value


class OTPVerifySerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=64)
    purpose = serializers.ChoiceField(choices=OTPPurpose.choices)
    code = serializers.RegexField(
        rf"^\d{{{settings.OTP_LENGTH}}}$",
        error_messages={"invalid": "کد OTP نامعتبر است."},
    )

    def validate_identifier(self, value):
        value = value.strip()
        return value.lower() if "@" in value else value


class PasswordResetSerializer(OTPVerifySerializer):
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )

    def validate_purpose(self, value):
        if value != OTPPurpose.RESET:
            raise serializers.ValidationError("purpose باید reset باشد.")
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if user is None:
            raise DomainError(
                "نام کاربری یا رمز عبور نادرست است.",
                code="invalid_credentials",
                status_code=401,
            )
        if not user.is_active:
            raise DomainError("حساب کاربری غیرفعال است.", code="inactive_user", status_code=401)
        if not user.is_verified:
            raise DomainError(
                "حساب کاربری هنوز تأیید نشده است.",
                code="user_not_verified",
                status_code=403,
            )
        attrs["user"] = user
        return attrs


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "phone",
            "is_verified",
            "first_name",
            "last_name",
        )
        read_only_fields = ("id", "is_verified")

    def update(self, instance, validated_data):
        old_email = instance.email
        old_phone = instance.phone
        instance = super().update(instance, validated_data)

        if instance.email != old_email or instance.phone != old_phone:
            instance.is_verified = False
            instance.save(update_fields=["is_verified"])

        return instance


def tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}
