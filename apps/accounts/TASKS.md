# اپ accounts — مالک اپ: مهیار · مالک `models.py` و migrationها: روزبه

## مدل‌ها — مالک: روزبه
- [ ] User سفارشی (phone/email/is_verified) + OTPPurpose + OTPRequestLog + migration اولیه — `feature/1-accounts-models` (**اولین چیزی که باید مرج شود؛ بدون آن پروژه بالا نمی‌آید**)

> مهیار `models.py` و migrationهای accounts را تغییر نمی‌دهد. اگر فیلد یا مدل جدیدی لازم شد، به روزبه بگوید تا در PR جدا اضافه شود.

## اجباری — مالک: مهیار
- [ ] ثبت‌نام و ورود با رمز عبور + JWT با SimpleJWT (access/refresh/rotate/blacklist) — `feature/11-accounts-jwt-auth`
- [ ] سامانه OTP: تولید، هش، TTL در Redis، سقف تلاش، throttle (scope="otp") — روی مدل OTPRequestLog تسک #1 — `feature/12-accounts-otp`
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

## Django admin — مالک: مهیار (بعد از مرج #1)
- [ ] `admin.py`: UserAdmin با فیلدهای phone/is_verified + OTPRequestLog فقط‌خواندنی — `feature/36-accounts-admin`

## امتیازی
- [ ] ورود با گوگل (allauth + dj-rest-auth) — `feature/29-google-oauth`

## وابستگی‌ها
خروجی این اپ (پرمیشن و توکن دسترسی) پیش‌نیاز اپ‌های forms و processes است → اول از همه مدل‌های accounts (#1، روزبه) و بعد JWT (#11) باید مرج شوند؛ مهیار بعد از مرج #1 شروع می‌کند.
