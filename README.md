# FormFlow API

An API-only backend for building dynamic forms, chaining them into multi-step processes, collecting responses, and analysing results in real time. Built with Django REST Framework.

![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/django-5.2-green)
![DRF](https://img.shields.io/badge/DRF-3.15-red)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## Features

### Forms
- Dynamic form builder with seven field types: **text, textarea, number, select, checkbox, rating, date**
- Per-field configuration and validation (length limits, regex, numeric ranges, option counts, date ranges, and more)
- Field ordering with a bulk-reorder endpoint, plus optional enforcement of answer order
- Response deadlines (`accepts_responses_until`) and an active/inactive switch
- Categories for organising forms and processes

### Responses
- Standard flow: **start** a submission, **save each answer incrementally**, then **finalize**
- Bulk or manual one-shot submission endpoint
- Anonymous (guest) and authenticated respondents
- Submission listing and **CSV / XLSX export**

### Processes
- Chain forms into ordered steps
- **Linear** processes (required previous steps must be completed first) or **free** processes (any order)
- Optional and required steps, with per-respondent run tracking and completion state

### Access Control
- Public or private forms and processes
- Private resources are protected by a password and an unlock endpoint that issues a short-lived signed access token (`X-Private-Access-Token`)
- Guest runs are tracked with `X-Session-Key`
- Owner-only management of forms, processes, reports, and schedules

### Authentication
- Registration with **OTP verification** (email / SMS via Kavenegar)
- Password login, password reset via OTP, and token refresh with rotation
- **Google sign-in** through django-allauth
- JWTs stored in `HttpOnly` cookies, with CSRF protection for unsafe requests
- Rate limiting on OTP, login, unlock, and submit endpoints

### Reports and Analytics
- Per-form and per-process reports: numeric stats (count, avg, min, max, sum), option distributions with percentages, date timelines, and text samples
- Paginated text answers
- Visit tracking, buffered in Redis and flushed to the database by a periodic task
- Dashboard overview stats
- **Scheduled reports** (weekly or monthly) delivered by email or signed webhook, with delivery logs
- **Live report updates** over WebSocket
- **GraphQL** endpoint for report queries
- Report caching with automatic invalidation

### Developer Experience
- OpenAPI schema with Swagger UI and ReDoc
- Postman collection and ERD included
- Docker setup for development and production (Nginx, Gunicorn, Daphne, Celery)
- CI with linting, migration checks, tests, and Docker build
- Optional Sentry error tracking

## Tech Stack

| Area | Technology |
|---|---|
| Framework | Django 5.2, Django REST Framework |
| Auth | SimpleJWT, django-allauth, dj-rest-auth |
| Database | PostgreSQL (SQLite supported for local use) |
| Cache / Broker | Redis |
| Background jobs | Celery, Celery Beat |
| Real time | Django Channels, Daphne |
| GraphQL | Strawberry GraphQL Django |
| API docs | drf-spectacular |
| Exports | openpyxl |
| Quality | pytest, pytest-django, factory-boy, ruff, black, pre-commit |
| Deployment | Docker, Nginx, Gunicorn |

## Getting Started

### Prerequisites
- Python 3.12
- Docker and Docker Compose (recommended)

### Run with Docker

```bash
cp .env.example .env
docker compose up --build -d db redis
docker compose run --rm web python manage.py migrate
docker compose up --build
```

This starts the API, a Celery worker, and Celery Beat. The API is available at `http://localhost:8000`.

### Run locally without Docker

```bash
cp .env.example .env
pip install -r requirements.txt
```

In `.env`, set:

```env
USE_SQLITE=True
USE_REDIS_CACHE=False
```

Then:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Configuration

All settings are read from environment variables. See [`.env.example`](.env.example) for the full list. Key groups:

| Group | Variables |
|---|---|
| Django | `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS` |
| Database | `DATABASE_URL`, `USE_SQLITE` |
| Redis / Celery | `REDIS_URL`, `CELERY_BROKER_URL`, `CHANNELS_REDIS_URL` |
| JWT / OTP | `JWT_ACCESS_MINUTES`, `OTP_LENGTH`, `OTP_TTL_SECONDS` |
| Email / SMS | `EMAIL_*`, `SMS_BACKEND`, `KAVENEGAR_API_KEY` |
| Google login | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| Private access | `PRIVATE_ACCESS_TOKEN_TTL_SECONDS`, `PRIVATE_ACCESS_TOKEN_SALT` |
| CORS / CSRF | `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` |
| Monitoring | `SENTRY_DSN` |

## API Overview

Interactive documentation is served at:

- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`

| Area | Endpoints |
|---|---|
| Auth | `/api/v1/auth/` register, otp/request, otp/verify, password/reset, login, logout, token/refresh, social/google, me |
| Categories | `/api/v1/categories/` |
| Forms | `/api/v1/forms/`, `/forms/{id}/fields/`, `/forms/{id}/fields/bulk-reorder/` |
| Submissions | `/api/v1/forms/{id}/submissions/`, `/forms/{id}/export/?format=csv\|xlsx` |
| Public forms | `/api/v1/public/forms/{uuid}/` with `unlock/`, `start/`, `submit/`, `submissions/{id}/answer/{field_id}/`, `submissions/{id}/finalize/` |
| Processes | `/api/v1/processes/`, `/processes/{id}/steps/` |
| Public processes | `/api/v1/public/processes/{uuid}/` with `unlock/`, `state/`, `steps/{step_id}/submit/` |
| Reports | `/api/v1/forms/{id}/report/`, `/api/v1/processes/{id}/report/`, `/api/v1/stats/overview/` |
| Schedules | `/api/v1/report-schedules/` |
| GraphQL | `/graphql/` |
| WebSocket | `/ws/reports/forms/{uuid}/` |

A ready-to-import Postman collection is available at [`Documents/FormFlow.postman_collection.json`](Documents/FormFlow.postman_collection.json).

## Authentication Notes

- Login endpoints set JWTs as `HttpOnly` cookies. Browsers send them automatically; unsafe requests must also send the CSRF cookie value in the `X-CSRFToken` header.
- For Google sign-in, the client completes Google OAuth2 and posts the Google `access_token` to `/api/v1/auth/social/google/`.
- For private forms and processes, call the `unlock/` endpoint, then send the returned token in `X-Private-Access-Token`. Guests also send the returned `session_key` in `X-Session-Key`.

## Testing and Code Quality

```bash
pytest
ruff check .
black --check apps config tests conftest.py manage.py
python manage.py makemigrations --check --dry-run
```

Tests run with `config.settings.test` and report coverage for the `apps` package.

## Production Deployment

Production uses `config.settings.production` and `docker-compose.prod.yml`, which runs:

- **web**: Gunicorn serving the REST API
- **daphne**: ASGI server for WebSockets
- **worker** and **beat**: Celery
- **nginx**: TLS termination on ports 80 and 443
- **db** and **redis**

Before starting the stack:

1. Set `DJANGO_ALLOWED_HOSTS`, `DJANGO_SECRET_KEY`, and the other production values in `.env`.
2. Replace `example.com` in [`deploy/nginx/default.conf`](deploy/nginx/default.conf).
3. Place your TLS certificates in `deploy/nginx/certs`.

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Migrations and static file collection run automatically on startup through `deploy/entrypoint.sh`.

## Project Structure

```
apps/
  accounts/     Users, OTP, JWT cookie auth, Google login
  categories/   Categories for forms and processes
  core/         Shared models, permissions, pagination, caching, exceptions
  forms/        Forms, dynamic field engine, submissions, export
  processes/    Multi-step processes and the step engine
  reports/      Aggregation, visits, schedules, WebSocket, tasks
  api/          URL routing and GraphQL
config/         Settings (base, local, test, production), Celery, ASGI/WSGI
deploy/         Nginx config and container entrypoint
docker/         Dockerfiles
Documents/      ERD, Postman collection, endpoint map
tests/          Shared test factories and infrastructure
```

## Contributing

Branch and pull request conventions are described in [`Documents/GIT_WORKFLOW.md`](Documents/GIT_WORKFLOW.md). Please make sure linting and tests pass before opening a pull request.

## License

Released under the [MIT License](LICENSE).
