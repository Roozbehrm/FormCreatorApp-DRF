# گردش‌کار گیت و گیت‌هاب

## ۱. مدل برنچینگ

```
main                      کد پایدار و قابل دیپلوی · protected
└── dev               برنچ یکپارچه‌سازی · protected · مقصد همه PRها
    ├── feature/<issue>-<slug>
    ├── fix/<issue>-<slug>
    ├── refactor/<issue>-<slug>
    ├── test/<issue>-<slug>
    ├── docs/<issue>-<slug>
    ├── chore/<issue>-<slug>
    └── release/v1.0        فقط قبل از تحویل: dev → release → main
```

قواعد ثابت:
- هیچ‌کس مستقیم روی `main` و `dev` پوش نمی‌کند.
- هر تسک = یک ایشو = یک برنچ = یک PR، و **`<issue>` در اسم برنچ همان شماره‌ی ایشو در گیت‌هاب است.**
- نام برنچ: `feature/8-forms-field-engine` (ایشو `#8`). توی PR بنویس `Closes #8`.
- مرج به `dev`: **Squash and merge** · مرج `release → main`: **Merge commit**
- قبل از باز کردن PR: `git fetch origin && git rebase origin/dev`
- برنچ بعد از مرج حذف می‌شود.

## ۲. لیست تسک‌ها و برنچ‌ها

لیست کامل ۳۵ تسک با مالک، اولویت، برنچ و وابستگی‌ها فقط در **`Documents/TASKS.md`** است
(عمداً اینجا تکرار نشده تا دو نسخه از هم جدا نیفتند). همه‌ی برنچ‌ها از اول روی ریموت ساخته شده‌اند.

> چون برنچ‌ها از قبل ساخته شده‌اند، **قبل از شروع هر تسک** حتماً:
> ```bash
> git fetch origin
> git switch feature/8-forms-field-engine
> git rebase origin/dev      # برنچ هنوز کامیتی ندارد، پس فقط جلو می‌رود
> ```
> وگرنه روی نسخه‌ی قدیمی dev (بدون مدل‌های پایه) کار می‌کنی.

تسک‌های `p0` پایه‌ی معماری هستند و باید قبل از بقیه مرج شوند —
ترتیب و جزئیات در `Documents/FOUNDATION_PLAN.md`.

## ۳. قرارداد کامیت (Conventional Commits)

```
feat(forms): add rating field handler with half-star support
fix(processes): prevent skipping locked step in linear process
test(reports): cover numeric aggregation edge cases
docs(api): annotate submission endpoints with extend_schema
chore(docker): add healthcheck for postgres service
```

اسکوپ‌های مجاز: `core, accounts, forms, processes, categories, reports, api, deploy, docs`

## ۴. تنظیمات ریپو (توسط روزبه)

- **Branch protection** روی `main` و `dev`:
  - حداقل ۱ ریویوی تأییدشده (برای `main` تأیید روزبه الزامی)
  - عبور موفق CI الزامی (چک‌های `lint` و `test`) — **بعد از مرج تسک‌های #1 و #4 روشنش کن**، قبلش پروژه بالا نمی‌آید و CI قرمز است
  - ممنوعیت force-push و حذف برنچ
  - نکته: روی ریپوی private، branch protection نیاز به پلن پولی (Team/Pro) دارد.
- **CODEOWNERS** فعال → ریویوئر خودکار بر اساس مسیر فایل (یوزرنیم‌های داخلش باید واقعی باشند)
- **Labels**: `p0` `p1` `p2` · `mandatory` · `bonus` · `blocked` · `needs-review` · `backend` · `infra` · `docs`
- **Project board**: Backlog → Todo → In Progress → In Review → Done

## ۵. روال روزانه هر عضو

```bash
git fetch origin
git switch feature/8-forms-field-engine      # برنچ از قبل ساخته شده
git rebase origin/dev
# ... کد + تست ...
git add -p && git commit -m "feat(forms): add number field handler"
git fetch origin && git rebase origin/dev
git push
# باز کردن PR به dev (Closes #8) → ریویو → squash merge
```

قوانین تیمی:
- هر PR حداکثر ۴۸ ساعت منتظر ریویو می‌ماند.
- PR بزرگ‌تر از ~۴۰۰ خط را بشکنید.
- کانفلیکت migration را با `python manage.py makemigrations --merge` حل کنید، نه با حذف فایل.

## نکته درباره‌ی ERD
محتوای `Documents/ERD.dbml` با آخرین وضعیت مدل‌ها هماهنگ است — ولی این هماهنگی خودکار نیست: هر بار
مدلی واقعاً عوض شود و کسی یادش برود `.dbml` را هم‌زمان آپدیت کند، این دو از هم جدا می‌افتند. پس قانون
ثابت می‌ماند: آپدیت `ERD.dbml` باید در همان PR همان تغییر مدل انجام شود، نه در یک برنچ جدا و دیرهنگام.
کاری که در تسک ۳۳ مانده فقط export گرفتن PNG از نسخه‌ی به‌روز همین DBML است.
