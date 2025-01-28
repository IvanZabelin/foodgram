#!/bin/bash

# Собрать статику
python manage.py collectstatic --noinput

cp -r /app/static/. /app/web/static

# Выполнить миграции
python manage.py migrate

# Запустить сервер
gunicorn --bind 0.0.0.0:8000 foodgram.wsgi
