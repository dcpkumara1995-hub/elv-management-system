#!/bin/sh

echo "Running database migrations..."

python manage.py migrate --noinput

echo "Starting Gunicorn..."

exec gunicorn --bind 0.0.0.0:8000 --workers 2 config.wsgi:application