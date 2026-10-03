from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("otp/request/", views.OTPRequestView.as_view(), name="otp-request"),
    path("otp/verify/", views.OTPVerifyView.as_view(), name="otp-verify"),
    path("password/reset/", views.PasswordResetView.as_view(), name="password-reset"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("social/google/", views.GoogleLoginView.as_view(), name="google-login"),
    path("token/refresh/", views.CookieTokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("me/", views.MeView.as_view(), name="me"),
]
