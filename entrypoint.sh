#!/bin/bash
# entrypoint.sh

# Wait for the PostgreSQL database to be ready
echo "Waiting for postgres..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Apply database migrations
echo "Applying database migrations"
python manage.py migrate --noinput --fake-initial

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# Start Gunicorn server
echo "Starting Gunicorn server"
exec gunicorn --bind :8000 --workers 2 django_project.wsgi:application
