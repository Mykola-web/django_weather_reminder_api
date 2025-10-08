#!/bin/sh
set -e  # exit immediately if a command fails

echo "Running migrations..."
python manage.py migrate

#makin 5 test users with 1 subscription each
python manage.py fake_data_maker

# Optional: create superuser from environment variables
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "$DJANGO_SUPERUSER_EMAIL" || true
fi

echo "Starting Gunicorn..."
exec "$@"
