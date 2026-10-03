# نقشه endpointها (v1)

| متد | مسیر | مالک |
|---|---|---|
| POST | `/api/v1/auth/register/` | مهیار |
| POST | `/api/v1/auth/otp/request/` | مهیار |
| POST | `/api/v1/auth/otp/verify/` | مهیار |
| POST | `/api/v1/auth/login/` | مهیار |
| POST | `/api/v1/auth/token/refresh/` | مهیار |
| POST | `/api/v1/auth/social/google/` | مهیار (امتیازی) |
| GET/PATCH | `/api/v1/auth/me/` | مهیار |
| CRUD | `/api/v1/categories/` | مهیار |
| CRUD | `/api/v1/forms/` | فائزه |
| CRUD | `/api/v1/forms/{id}/fields/` (+ `bulk-reorder`) | فائزه |
| GET | `/api/v1/forms/{id}/submissions/` | فائزه |
| GET | `/api/v1/forms/{id}/export/?format=csv` | فائزه |
| GET | `/api/v1/forms/{id}/report/` | علی |
| GET | `/api/v1/public/forms/{uuid}/` | فائزه |
| POST | `/api/v1/public/forms/{uuid}/unlock/` | مهیار |
| POST | `/api/v1/public/forms/{uuid}/submit/` (فقط وارد کردن دستی/دسته‌ای) | فائزه |
| POST | `/api/v1/public/forms/{uuid}/start/` (شروع پاسخ، مسیر استاندارد) | فائزه |
| POST | `/api/v1/public/forms/{uuid}/submissions/{submission_id}/answer/{field_id}/` (ذخیره‌ی تدریجی هر سوال) | فائزه |
| POST | `/api/v1/public/forms/{uuid}/submissions/{submission_id}/finalize/` (اتمام پاسخ‌دهی) | فائزه |
| CRUD | `/api/v1/processes/` | روزبه |
| CRUD | `/api/v1/processes/{id}/steps/` | روزبه |
| GET | `/api/v1/processes/{id}/report/` | علی |
| GET | `/api/v1/public/processes/{uuid}/` | روزبه |
| POST | `/api/v1/public/processes/{uuid}/unlock/` | مهیار |
| GET | `/api/v1/public/processes/{uuid}/state/` | روزبه |
| POST | `/api/v1/public/processes/{uuid}/steps/{step_id}/submit/` | روزبه |
| CRUD | `/api/v1/report-schedules/` | علی |
| GET | `/api/v1/stats/overview/` | علی |
| WS | `/ws/reports/forms/{uuid}/` | علی (امتیازی) |
| POST | `/graphql/` | علی (امتیازی) |
| GET | `/api/schema/swagger-ui/` · `/api/schema/redoc/` | تیم |

برای ورود گوگل، کلاینت ابتدا OAuth2 را با گوگل کامل می‌کند و سپس `access_token` را به‌صورت JSON به `/api/v1/auth/social/google/` می‌فرستد. در پاسخ، JWTها فقط در کوکی‌های `HttpOnly` قرار می‌گیرند.
