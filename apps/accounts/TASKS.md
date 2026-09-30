# اپ accounts — مالک: مهیار

## اجباری
- [ ] مدل User سفارشی (phone/email/is_verified) + migration اولیه — `feature/1-accounts-user-model` (**اولین چیزی که باید مرج شود؛ بدون آن پروژه بالا نمی‌آید**)
- [ ] ثبت‌نام و ورود با رمز عبور + JWT با SimpleJWT (access/refresh/rotate/blacklist) — `feature/11-accounts-jwt-auth`
- [ ] سامانه OTP: تولید، هش، TTL در Redis، سقف تلاش، throttle (scope="otp") + مدل OTPRequestLog — `feature/12-accounts-otp`
- [ ] ارسال OTP با Celery (ایمیل + قلاب SMS) — `feature/13-accounts-otp-celery`
- [ ] مکانیزم گذرواژه فرم/فرایند خصوصی: endpoint unlock → توکن موقت دسترسی (JWT کوتاه‌عمر یا امضای HMAC) — هماهنگ با فائزه و روزبه — `feature/18-private-access-password`
## تست
- [ ] ثبت‌نام با ایمیل/شماره تکراری رد می‌شود
- [ ] OTP درست پذیرفته می‌شود و کد بلافاصله بعدش دیگر معتبر نیست (یک‌بارمصرف)
- [ ] OTP غلط: شمارنده‌ی attempts بالا می‌رود، بعد از سقف (`OTP_MAX_ATTEMPTS`) قفل می‌شود (۴۲۹)
- [ ] OTP منقضی‌شده (بعد از `OTP_TTL_SECONDS`) رد می‌شود
- [ ] throttle روی `scope="otp"` واقعاً محدود می‌کند (تست با چند درخواست پشت‌سرهم)
- [ ] لاگین موفق access+refresh می‌دهد؛ رفرش توکن، توکن قبلی را rotate/blacklist می‌کند
- [ ] endpoint unlock فرم/فرایند خصوصی: گذرواژه‌ی درست توکن موقت می‌دهد، غلط رد می‌شود، توکن بعد از انقضا کار نمی‌کند

## امتیازی
- [ ] ورود با گوگل (allauth + dj-rest-auth) — `feature/29-google-oauth`

## وابستگی‌ها
خروجی این اپ (پرمیشن و توکن دسترسی) پیش‌نیاز اپ‌های forms و processes است → اول از همه مدل User (#1) و بعد JWT (#11) باید مرج شوند.
