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
| روزبه | لید — پایه معماری، فرایندها، زیرساخت | 18 | #1, #2, #3, #4, #5, #6, #7, #8, #9, #10, #19, #20, #26, #27, #28, #33, #35, #39 |
| مهیار | احراز هویت، دسترسی، دسته‌بندی | 10 | #11, #12, #13, #14, #18, #29, #30, #34, #36, #37 |
| فائزه | فرم‌ساز (CRUD/API روی پایه‌ی روزبه) | 6 | #15, #16, #17, #25, #31, #38 |
| علی | گزارش‌گیری (بازدید، کش، زمان‌بندی) | 6 | #21, #22, #23, #24, #32, #40 |

##  روزبه — لید — پایه معماری، فرایندها، زیرساخت

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>تسک</th>
      <th>اولویت</th>
      <th>نوع</th>
      <th>برنچ</th>
      <th>وابسته به</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>مدل‌های اپ accounts: User سفارشی (phone/email/is_verified) + OTPPurpose + OTPRequestLog + migration اولیه — <strong>بلاک‌کننده‌ی کل پروژه</strong> چون <code>AUTH_USER_MODEL</code> به آن اشاره دارد. کل <code>accounts/models.py</code></td>
      <td>p0</td>
      <td>اجباری</td>
      <td><code>feature/1-accounts-models</code></td>
      <td style="white-space: nowrap;">#3</td>
    </tr>
    <tr>
      <td>2</td>
      <td>راه‌اندازی ریپو، ساختار پوشه‌ها، تنظیمات سه‌لایه، <bdi dir="ltr"><code>.env.example</code></bdi>، Docker + docker-compose (dev/prod) + entrypoint</td>
      <td>p0</td>
      <td>اجباری</td>
      <td><code>feature/2-project-setup-docker</code></td>
      <td style="white-space: nowrap;">#1</td>
    </tr>
    <tr>
      <td>3</td>
      <td>اپ <code>core</code>: مدل‌های پایه (models.py)</td>
      <td>p0</td>
      <td>اجباری</td>
      <td><code>feature/3-core-base-models</code></td>
      <td style="white-space: nowrap;">—</td>
    </tr>
    <tr>
      <td>4</td>
      <td>اپ <code>core</code>: exception handler، pagination، پرمیشن، کش — <strong>بلاک‌کننده:</strong> <code>REST_FRAMEWORK</code> در settings به آن‌ها اشاره می‌کند</td>
      <td>p0</td>
      <td>اجباری</td>
      <td><code>feature/4-core-utils</code></td>
      <td style="white-space: nowrap;">—</td>
    </tr>
    <tr>
      <td>5</td>
      <td>زیرساخت مشترک تست (conftest، factory-boy، تأیید آستانه پوشش در CI)</td>
      <td>p0</td>
      <td>اجباری</td>
      <td><code>chore/5-test-infrastructure</code></td>
      <td style="white-space: nowrap;">#1</td>
    </tr>
    <tr>
      <td>6</td>
      <td>GitHub Actions، branch protection، CODEOWNERS، برد پروژه</td>
      <td>p0</td>
      <td>اجباری</td>
      <td><code>chore/6-ci-github-actions</code></td>
      <td style="white-space: nowrap;">—</td>
    </tr>
    <tr>
      <td>7</td>
      <td>مدل‌های Form/Field/FieldOption/Submission/Answer/AnswerOption</td>
      <td>p0</td>
      <td>اجباری</td>
      <td><code>feature/7-forms-models</code></td>
      <td style="white-space: nowrap;">#1, #3</td>
    </tr>
    <tr>
      <td>8</td>
      <td>موتور فیلد پویا (BaseFieldHandler + FieldRegistry + هفت هندلر) + submit_form + مسیر ذخیره‌ی تدریجی</td>
      <td>p0</td>
      <td>اجباری</td>
      <td><code>feature/8-forms-field-engine</code></td>
      <td style="white-space: nowrap;">#7</td>
    </tr>
    <tr>
      <td>9</td>
      <td>مدل‌های Process/ProcessStep/ProcessRun/StepCompletion</td>
      <td>p0</td>
      <td>اجباری</td>
      <td><code>feature/9-processes-models</code></td>
      <td style="white-space: nowrap;">#3, #7</td>
    </tr>
    <tr>
      <td>10</td>
      <td>مدل‌های VisitCounter/ReportSchedule/ReportDelivery + موتور تجمیع گزارش</td>
      <td>p0</td>
      <td>اجباری</td>
      <td><code>feature/10-reports-aggregation</code></td>
      <td style="white-space: nowrap;">#7, #9</td>
    </tr>
    <tr>
      <td>19</td>
      <td>موتور فرایند خطی (قفل مرحله) و آزاد</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>feature/19-processes-linear-engine</code></td>
      <td style="white-space: nowrap;">#8, #9</td>
    </tr>
    <tr>
      <td>20</td>
      <td>API عمومی فرایند + endpoint وضعیت پیشروی</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>feature/20-processes-public-api</code></td>
      <td style="white-space: nowrap;">#19</td>
    </tr>
    <tr>
      <td>26</td>
      <td>Nginx + gunicorn + collectstatic در پروداکشن</td>
      <td>p2</td>
      <td>اجباری</td>
      <td><code>chore/26-nginx-production</code></td>
      <td style="white-space: nowrap;">#2</td>
    </tr>
    <tr>
      <td>27</td>
      <td><strong>امتیازی:</strong> گزارش برخط با WebSocket (Channels consumer + routing)</td>
      <td>p2</td>
      <td>امتیازی</td>
      <td><code>feature/27-reports-realtime-ws</code></td>
      <td style="white-space: nowrap;">#10</td>
    </tr>
    <tr>
      <td>28</td>
      <td><strong>امتیازی:</strong> GraphQL read-only روی گزارش‌ها</td>
      <td>p2</td>
      <td>امتیازی</td>
      <td><code>feature/28-graphql-reports</code></td>
      <td style="white-space: nowrap;">#10</td>
    </tr>
    <tr>
      <td>33</td>
      <td>export گرفتن PNG از <code>Documents/ERD.dbml</code> (نسخه‌ی به‌روز)</td>
      <td>p2</td>
      <td>اجباری</td>
      <td><code>docs/33-erd-export</code></td>
      <td style="white-space: nowrap;">#7, #9, #10</td>
    </tr>
    <tr>
      <td>35</td>
      <td>README نهایی و بازبینی مستندات</td>
      <td>p2</td>
      <td>اجباری</td>
      <td><code>docs/35-final-readme</code></td>
      <td style="white-space: nowrap;">—</td>
    </tr>
    <tr>
      <td>39</td>
      <td>ادمین processes: Process با inline برای ProcessStep؛ ProcessRun/StepCompletion فقط‌خواندنی</td>
      <td>p2</td>
      <td>اجباری</td>
      <td><code>feature/39-processes-admin</code></td>
      <td style="white-space: nowrap;">#9</td>
    </tr>
  </tbody>
</table>

> تسک‌های `p0` «پایه معماری»اند و باید قبل از اینکه بقیه سراغ CRUD و سرویس‌های خودشان بروند تمام و مرج شوند؛
> ترتیب دقیق در `Documents/FOUNDATION_PLAN.md`. تسک #1 (مدل‌های accounts) و #4 (core utils) از همه مهم‌ترند: پروژه تا این دو مرج نشوند بالا نمی‌آید.
> کل `apps/accounts/models.py` و migrationهای آن با روزبه است (تا روزبه منتظر مهیار نماند)؛ مهیار بقیه‌ی اپ accounts را بعد از مرج #1 می‌سازد.

##  مهیار — احراز هویت، دسترسی، دسته‌بندی

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>تسک</th>
      <th>اولویت</th>
      <th>نوع</th>
      <th>برنچ</th>
      <th>وابسته به</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>11</td>
      <td>ثبت‌نام/ورود + JWT (SimpleJWT، rotate، blacklist)</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>feature/11-accounts-jwt-auth</code></td>
      <td style="white-space: nowrap;">#1</td>
    </tr>
    <tr>
      <td>12</td>
      <td>سامانه OTP: Redis + TTL + سقف تلاش + throttle (روی مدل OTPRequestLog که در #1 ساخته می‌شود)</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>feature/12-accounts-otp</code></td>
      <td style="white-space: nowrap;">#1, #3</td>
    </tr>
    <tr>
      <td>13</td>
      <td>ارسال OTP با Celery (ایمیل + قلاب SMS)</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>feature/13-accounts-otp-celery</code></td>
      <td style="white-space: nowrap;">#12</td>
    </tr>
    <tr>
      <td>14</td>
      <td>اپ categories: مدل + CRUD + درخت + فیلتر</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>feature/14-categories-crud</code></td>
      <td style="white-space: nowrap;">#1, #3</td>
    </tr>
    <tr>
      <td>18</td>
      <td>مکانیزم گذرواژه فرم/فرایند خصوصی (endpoint unlock + توکن موقت) — شامل <code>apps/core/access.py</code> (توکن مشترک forms/processes)</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>feature/18-private-access-password</code></td>
      <td style="white-space: nowrap;">#4, #7, #11</td>
    </tr>
    <tr>
      <td>29</td>
      <td><strong>امتیازی:</strong> ورود با گوگل (OAuth2)</td>
      <td>p2</td>
      <td>امتیازی</td>
      <td><code>feature/29-google-oauth</code></td>
      <td style="white-space: nowrap;">#11</td>
    </tr>
    <tr>
      <td>30</td>
      <td>امنیت: CORS، throttle، هدرهای امن</td>
      <td>p2</td>
      <td>اجباری</td>
      <td><code>feature/30-security-hardening</code></td>
      <td style="white-space: nowrap;">#11</td>
    </tr>
    <tr>
      <td>34</td>
      <td>Postman collection</td>
      <td>p2</td>
      <td>اجباری</td>
      <td><code>docs/34-postman-collection</code></td>
      <td style="white-space: nowrap;">#16, #20, #21</td>
    </tr>
    <tr>
      <td>36</td>
      <td>ادمین accounts: UserAdmin (با phone/is_verified) + OTPRequestLog فقط‌خواندنی</td>
      <td>p2</td>
      <td>اجباری</td>
      <td><code>feature/36-accounts-admin</code></td>
      <td style="white-space: nowrap;">#1</td>
    </tr>
    <tr>
      <td>37</td>
      <td>ادمین categories: Category (list_display، جستجو)</td>
      <td>p2</td>
      <td>اجباری</td>
      <td><code>feature/37-categories-admin</code></td>
      <td style="white-space: nowrap;">#14</td>
    </tr>
  </tbody>
</table>

##  فائزه — فرم‌ساز (CRUD/API روی پایه‌ی روزبه)

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>تسک</th>
      <th>اولویت</th>
      <th>نوع</th>
      <th>برنچ</th>
      <th>وابسته به</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>15</td>
      <td>CRUD فرم و فیلد + bulk reorder + لینک یکتا</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>feature/15-forms-crud-api</code></td>
      <td style="white-space: nowrap;">#4, #7, #8</td>
    </tr>
    <tr>
      <td>16</td>
      <td>اسکیمای عمومی فرم (خروجی کش‌شده برای پاسخ‌دهنده) + endpoint ثبت پاسخ عمومی</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>feature/16-forms-public-submit</code></td>
      <td style="white-space: nowrap;">#8, #15</td>
    </tr>
    <tr>
      <td>17</td>
      <td>تکمیل قوانین دقیق اعتبارسنجی هر هفت نوع فیلد (روی موتور پایه‌ی #8)</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>feature/17-forms-field-validation</code></td>
      <td style="white-space: nowrap;">#8</td>
    </tr>
    <tr>
      <td>25</td>
      <td>مشاهده پاسخ‌های ارسالی + خروجی CSV/Excel</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>feature/25-forms-export-csv</code></td>
      <td style="white-space: nowrap;">#16</td>
    </tr>
    <tr>
      <td>31</td>
      <td>تست کامل هر هفت نوع فیلد (happy + edge)</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>test/31-forms-field-tests</code></td>
      <td style="white-space: nowrap;">#17</td>
    </tr>
    <tr>
      <td>38</td>
      <td>ادمین forms: Form/Field/Submission (inline برای Field و FieldOption؛ Submission فقط‌خواندنی)</td>
      <td>p2</td>
      <td>اجباری</td>
      <td><code>feature/38-forms-admin</code></td>
      <td style="white-space: nowrap;">#7</td>
    </tr>
  </tbody>
</table>

##  علی — گزارش‌گیری (بازدید، کش، زمان‌بندی)

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>تسک</th>
      <th>اولویت</th>
      <th>نوع</th>
      <th>برنچ</th>
      <th>وابسته به</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>21</td>
      <td>endpoint مشاهده گزارش فرم/فرایند (روی aggregate_field/form_report آماده‌ی #10)</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>feature/21-reports-view-api</code></td>
      <td style="white-space: nowrap;">#10</td>
    </tr>
    <tr>
      <td>22</td>
      <td>شمارش بازدید با Redis + تسک flush + تعداد پاسخ</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>feature/22-reports-visits</code></td>
      <td style="white-space: nowrap;">#10</td>
    </tr>
    <tr>
      <td>23</td>
      <td>لایه کش نتایج تجمیع + ابطال با سیگنال ثبت پاسخ (هماهنگ با core/cache.py)</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>feature/23-reports-cache</code></td>
      <td style="white-space: nowrap;">#4, #10</td>
    </tr>
    <tr>
      <td>24</td>
      <td>گزارش دوره‌ای: Celery Beat + ایمیل + webhook با HMAC + retry + لاگ ارسال</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>feature/24-reports-schedule-celery</code></td>
      <td style="white-space: nowrap;">#10</td>
    </tr>
    <tr>
      <td>32</td>
      <td>تست‌های reports</td>
      <td>p1</td>
      <td>اجباری</td>
      <td><code>test/32-reports-tests</code></td>
      <td style="white-space: nowrap;">#21, #22, #23, #24</td>
    </tr>
    <tr>
      <td>40</td>
      <td>ادمین reports: ReportSchedule/ReportDelivery/VisitCounter (لاگ‌ها فقط‌خواندنی)</td>
      <td>p2</td>
      <td>اجباری</td>
      <td><code>feature/40-reports-admin</code></td>
      <td style="white-space: nowrap;">#10</td>
    </tr>
  </tbody>
</table>

## مسئولیت‌های مستمر (ایشو ندارند)

- **روزبه:** ریویو همه‌ی PRها و مرج به `dev`؛ هماهنگی `.env.example` با متغیرهای محیطی جدید.
- **هر نفر:** endpointهای خودش را با `@extend_schema` مستند کند و حداقل ۷۰٪ پوشش تست برای اپ خودش داشته باشد.
- **ERD:** `Documents/ERD.dbml` باید با مدل‌ها هماهنگ بماند؛ هر تغییر واقعی مدل در **همان PR** اینجا هم اعمال شود.
  تسک ۳۳ فقط export گرفتن PNG است.
- **ادمین:** هر اپ `admin.py` خودش را دارد و مالک اپ می‌نویسد (تسک‌های ۳۶ تا ۴۰)؛ هر کدام بعد از مرج مدل‌های همان اپ.

## اتمام کار

کد + تست + مستندسازی API + بدون خطای ruff/black + migration کامیت‌شده + ریویو شده + مرج در `dev`.
