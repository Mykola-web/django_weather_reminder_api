#!/bin/sh
# entrypoint.sh

# run migraions
echo "Applying database migrations..."
python manage.py migrate --noinput

# run gunicorn
echo "Starting Gunicorn..."
exec gunicorn weather_project.wsgi:application --bind 0.0.0.0:$PORT --workers 2
