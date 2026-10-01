# داکر و زیرساخت — مالک: روزبه

برنچ: `feature/2-project-setup-docker` (پایه) + `chore/22-nginx-production` (پروداکشن)

## توسعه (dev)
- [ ] `docker/Dockerfile.dev` — ایمیج dev با نصب `requirements.txt` کامل
- [ ] `docker-compose.yml` — سرویس‌های db/redis/web/worker/beat برای توسعه
- [ ] بررسی این‌که `docker compose up -d --build` بدون خطا بالا می‌آید

## پروداکشن
- [ ] `docker/Dockerfile` — ایمیج prod (چندمرحله‌ای در صورت نیاز برای کوچک‌ماندن)
- [ ] `deploy/entrypoint.sh` — اجرای خودکار `migrate` و `collectstatic` قبل از استارت
- [ ] `docker-compose.prod.yml` — اضافه‌شدن سرویس‌های `daphne` و `nginx` نسبت به dev
- [ ] `deploy/nginx/default.conf` — روتینگ `/static/`, `/media/`, `/ws/` و بقیه به `web`/`daphne`
- [ ] تست کامل: `docker compose -f docker-compose.prod.yml up -d --build` روی یک سرور تمیز

## هماهنگی با بقیه
- هر متغیر محیطی جدیدی که مهیار/فائزه/علی در کدشان اضافه می‌کنند باید به `.env.example` هم اضافه شود —
  این تسک تیمی است، ولی هماهنگی نهایی‌اش با روزبه.
