# تسک‌بندی کامل تیم

**منبع واحد تسک‌ها همین فایل است.** هر ردیف = یک ایشو = یک برنچ = یک PR، و سه شماره یکی هستند:

> شماره‌ی تسک = شماره‌ی ایشو در گیت‌هاب = شماره‌ی توی اسم برنچ

مثال: تسک ۸ ← ایشو `#8` ← برنچ `feature/8-forms-field-engine` ← PR با `Closes #8`.
شماره‌ها **سراسری** هستند (بین چهار نفر تکراری نیستند)، برای همین در جدول هر نفر پشت‌سرهم نیستند.

- اسکریپت راه‌انداز ایشوها را به ترتیب شماره می‌سازد و اگر شماره‌ی ایشو با شماره‌ی تسک نخواند متوقف می‌شود.
  برای همین **قبل از راه‌اندازی هیچ ایشو یا PR دستی در ریپو نساز** (گیت‌هاب شماره‌ی ایشو و PR را از یک شمارنده می‌دهد).
- تسک‌هایی که بعداً پیدا می‌شوند: اول ایشو بساز، بعد برنچ را با همان شماره‌ی ایشو (`fix/41-...`) بساز.
- **اولویت:** `p0` = پایه‌ی معماری، باید قبل از بقیه مرج شود · `p1` = کار اصلی روی پایه · `p2` = تکمیلی و امتیازی.
  زمان‌بندی ثابتی نداریم؛ ترتیب کار فقط با اولویت و ستون «وابسته به» تعیین می‌شود.
- چک‌لیست جزئی هر تسک در فایل `TASKS.md` داخل پوشه‌ی همان اپ است.
- ترتیب مرج تسک‌های پایه: `Documents/FOUNDATION_PLAN.md`

## خلاصه: هر نفر چه تسک‌هایی دارد

| نفر | نقش | تعداد | شماره‌ی تسک‌ها |
|---|---|---|---|
| روزبه | لید — پایه معماری، فرایندها، زیرساخت | 16 | #2, #3, #4, #5, #6, #7, #8, #9, #10, #19, #20, #26, #27, #28, #33, #35 |
| مهیار | احراز هویت، دسترسی، دسته‌بندی | 9 | #1, #11, #12, #13, #14, #18, #29, #30, #34 |
| فائزه | فرم‌ساز (CRUD/API روی پایه‌ی روزبه) | 5 | #15, #16, #17, #25, #31 |
| علی | گزارش‌گیری (بازدید، کش، زمان‌بندی) | 5 | #21, #22, #23, #24, #32 |

##  روزبه — لید — پایه معماری، فرایندها، زیرساخت

| # | تسک | اولویت | نوع | برنچ | وابسته به |
|---|---|---|---|---|---|
| 2 | راه‌اندازی ریپو، ساختار پوشه‌ها، تنظیمات سه‌لایه، `.env.example`، Docker + docker-compose (dev/prod) + entrypoint | p0 | اجباری | `feature/2-project-setup-docker` | #1 |
| 3 | اپ `core`: مدل‌های پایه (models.py) | p0 | اجباری | `feature/3-core-base-models` | — |
| 4 | اپ `core`: exception handler، pagination، پرمیشن، کش — **بلاک‌کننده:** `REST_FRAMEWORK` در settings به آن‌ها اشاره می‌کند | p0 | اجباری | `feature/4-core-utils` | — |
| 5 | زیرساخت مشترک تست (conftest، factory-boy، تأیید آستانه پوشش در CI) | p0 | اجباری | `chore/5-test-infrastructure` | #1 |
| 6 | GitHub Actions، branch protection، CODEOWNERS، برد پروژه | p0 | اجباری | `chore/6-ci-github-actions` | — |
| 7 | مدل‌های Form/Field/FieldOption/Submission/Answer/AnswerOption | p0 | اجباری | `feature/7-forms-models` | #1 #3 |
| 8 | موتور فیلد پویا (BaseFieldHandler + FieldRegistry + هفت هندلر) + submit_form + مسیر ذخیره‌ی تدریجی | p0 | اجباری | `feature/8-forms-field-engine` | #7 |
| 9 | مدل‌های Process/ProcessStep/ProcessRun/StepCompletion | p0 | اجباری | `feature/9-processes-models` | #3 #7 |
| 10 | مدل‌های VisitCounter/ReportSchedule/ReportDelivery + موتور تجمیع گزارش | p0 | اجباری | `feature/10-reports-aggregation` | #7 #9 |
| 19 | موتور فرایند خطی (قفل مرحله) و آزاد | p1 | اجباری | `feature/19-processes-linear-engine` | #8 #9 |
| 20 | API عمومی فرایند + endpoint وضعیت پیشروی | p1 | اجباری | `feature/20-processes-public-api` | #19 |
| 26 | Nginx + gunicorn + collectstatic در پروداکشن | p2 | اجباری | `chore/26-nginx-production` | #2 |
| 27 | **امتیازی:** گزارش برخط با WebSocket (Channels consumer + routing) | p2 | امتیازی | `feature/27-reports-realtime-ws` | #10 |
| 28 | **امتیازی:** GraphQL read-only روی گزارش‌ها | p2 | امتیازی | `feature/28-graphql-reports` | #10 |
| 33 | export گرفتن PNG از `Documents/ERD.dbml` (نسخه‌ی به‌روز) | p2 | اجباری | `docs/33-erd-export` | #7 #9 #10 |
| 35 | README نهایی و بازبینی مستندات | p2 | اجباری | `docs/35-final-readme` | — |

> تسک‌های `p0` «پایه معماری»اند و باید قبل از اینکه بقیه سراغ CRUD و سرویس‌های خودشان بروند تمام و مرج شوند؛
> ترتیب دقیق در `Documents/FOUNDATION_PLAN.md`. تسک #1 (مدل User) با اینکه مال مهیار است، از همه مهم‌تر است.

##  مهیار — احراز هویت، دسترسی، دسته‌بندی

| # | تسک | اولویت | نوع | برنچ | وابسته به |
|---|---|---|---|---|---|
| 1 | مدل User سفارشی (phone/email/is_verified) + migration اولیه — **بلاک‌کننده‌ی کل پروژه** چون `AUTH_USER_MODEL` به آن اشاره دارد | p0 | اجباری | `feature/1-accounts-user-model` | — |
| 11 | ثبت‌نام/ورود + JWT (SimpleJWT، rotate، blacklist) | p1 | اجباری | `feature/11-accounts-jwt-auth` | #1 |
| 12 | سامانه OTP: Redis + TTL + سقف تلاش + throttle + مدل OTPRequestLog | p1 | اجباری | `feature/12-accounts-otp` | #1 #3 |
| 13 | ارسال OTP با Celery (ایمیل + قلاب SMS) | p1 | اجباری | `feature/13-accounts-otp-celery` | #12 |
| 14 | اپ categories: مدل + CRUD + درخت + فیلتر | p1 | اجباری | `feature/14-categories-crud` | #1 #3 |
| 18 | مکانیزم گذرواژه فرم/فرایند خصوصی (endpoint unlock + توکن موقت) | p1 | اجباری | `feature/18-private-access-password` | #7 #11 |
| 29 | **امتیازی:** ورود با گوگل (OAuth2) | p2 | امتیازی | `feature/29-google-oauth` | #11 |
| 30 | امنیت: CORS، throttle، هدرهای امن | p2 | اجباری | `feature/30-security-hardening` | #11 |
| 34 | Postman collection | p2 | اجباری | `docs/34-postman-collection` | #16 #20 #21 |

##  فائزه — فرم‌ساز (CRUD/API روی پایه‌ی روزبه)

| # | تسک | اولویت | نوع | برنچ | وابسته به |
|---|---|---|---|---|---|
| 15 | CRUD فرم و فیلد + bulk reorder + لینک یکتا | p1 | اجباری | `feature/15-forms-crud-api` | #4 #7 #8 |
| 16 | اسکیمای عمومی فرم (خروجی کش‌شده برای پاسخ‌دهنده) + endpoint ثبت پاسخ عمومی | p1 | اجباری | `feature/16-forms-public-submit` | #8 #15 |
| 17 | تکمیل قوانین دقیق اعتبارسنجی هر هفت نوع فیلد (روی موتور پایه‌ی #8) | p1 | اجباری | `feature/17-forms-field-validation` | #8 |
| 25 | مشاهده پاسخ‌های ارسالی + خروجی CSV/Excel | p1 | اجباری | `feature/25-forms-export-csv` | #16 |
| 31 | تست کامل هر هفت نوع فیلد (happy + edge) | p1 | اجباری | `test/31-forms-field-tests` | #17 |

##  علی — گزارش‌گیری (بازدید، کش، زمان‌بندی)

| # | تسک | اولویت | نوع | برنچ | وابسته به |
|---|---|---|---|---|---|
| 21 | endpoint مشاهده گزارش فرم/فرایند (روی aggregate_field/form_report آماده‌ی #10) | p1 | اجباری | `feature/21-reports-view-api` | #10 |
| 22 | شمارش بازدید با Redis + تسک flush + تعداد پاسخ | p1 | اجباری | `feature/22-reports-visits` | #10 |
| 23 | لایه کش نتایج تجمیع + ابطال با سیگنال ثبت پاسخ (هماهنگ با core/cache.py) | p1 | اجباری | `feature/23-reports-cache` | #4 #10 |
| 24 | گزارش دوره‌ای: Celery Beat + ایمیل + webhook با HMAC + retry + لاگ ارسال | p1 | اجباری | `feature/24-reports-schedule-celery` | #10 |
| 32 | تست‌های reports | p1 | اجباری | `test/32-reports-tests` | #21 #22 #23 #24 |

## مسئولیت‌های مستمر (ایشو ندارند)

- **روزبه:** ریویو همه‌ی PRها و مرج به `dev`؛ هماهنگی `.env.example` با متغیرهای محیطی جدید.
- **هر نفر:** endpointهای خودش را با `@extend_schema` مستند کند و حداقل ۷۰٪ پوشش تست برای اپ خودش داشته باشد.
- **ERD:** `Documents/ERD.dbml` باید با مدل‌ها هماهنگ بماند؛ هر تغییر واقعی مدل در **همان PR** اینجا هم اعمال شود.
  تسک ۳۳ فقط export گرفتن PNG است.

## اتمام

کد + تست + مستندسازی API + بدون خطای ruff/black + migration کامیت‌شده + ریویو شده + مرج در `dev`.
