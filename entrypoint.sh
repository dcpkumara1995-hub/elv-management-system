#!/bin/sh

echo "Running database migrations..."

python manage.py migrate --noinput

echo "Creating Admin user..."

python manage.py shell -c "from django.contrib.auth.models import User; u, created = User.objects.get_or_create(username='Admin'); u.set_password('Admin@#123'); u.is_superuser=True; u.is_staff=True; u.is_active=True; u.save(); print('Admin user ready')"

echo "Starting Gunicorn..."

exec gunicorn --bind 0.0.0.0:8000 --workers 2 config.wsgi:application