#!/bin/bash

# Собрать статику
python manage.py collectstatic
cp -r /app/static/. web/static

# Выполнить миграции
python manage.py makemigrations
python manage.py migrate

# Создать суперпользователя
echo "from django.contrib.auth import get_user_model; User = get_user_model();
User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')" | python manage.py shell

# Создать теги
add_tag() {
    name="$1"
    slug="$2"

    echo "from recipes.models import Tag;
Tag.objects.create(name='$name', slug='$slug')" | python manage.py shell
}
add_tag "Завтрак" "breakfast"
add_tag "Обед" "lunch"
add_tag "Ужин" "dinner"

# Запустить сервер
gunicorn --bind 0.0.0.0:8000 foodgram.wsgi