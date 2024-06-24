#!/bin/sh

#sleep 10
python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py collectstatic --noinput
gunicorn --bind 0.0.0.0:8000 --workers 3 website.wsgi:application