"""
مالک: مهیار
TODO:
  - RegisterView            POST /auth/register/
  - OTPRequestView          POST /auth/otp/request/     throttle_scope = "otp"
  - OTPVerifyView           POST /auth/otp/verify/      -> JWT
  - LoginView / TokenRefreshView
  - GoogleLoginView         GET  /auth/social/google/   (امتیازی)
  - MeView                  GET/PATCH /auth/me/
هر ویو باید @extend_schema داشته باشد.
"""
