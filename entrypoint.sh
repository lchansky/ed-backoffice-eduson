#!/bin/sh

python manage.py collectstatic --no-input
cp /proj/static_for_build/favicon.ico /proj/src/staticfiles/favicon.ico
python manage.py migrate --no-input
python manage.py init_courses  # Кастомная команда

DJANGO_SUPERUSER_PASSWORD=$SUPER_USER_PASSWORD python manage.py createsuperuser --username $SUPER_USER_NAME --email $SUPER_USER_EMAIL --noinput

gunicorn proj.wsgi:application --bind 0.0.0.0:5000