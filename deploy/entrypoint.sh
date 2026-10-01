#!/bin/sh
set -e
echo "waiting for postgres..."
while ! nc -z "${POSTGRES_HOST:-db}" "${POSTGRES_PORT:-5432}"; do sleep 0.5; done

python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec "$@"
