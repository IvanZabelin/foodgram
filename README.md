# Продуктовый помощник Foodgram

***
- [Описание](#описание)
- [Запуск проекта локально](#запуск-проекта-локально)
- [Запуск проекта на удаленном сервере](#запуск-проекта-на-удаленном-сервере)
- [GitHub Actions](#github-actions)
- [Демонстрационные данные](#демонстрационные-данные)
***

## Описание
«Фудграм» — сайт, на котором пользователи публикуют рецепты, добавляют 
чужие рецепты в избранное и подписываются на публикации других авторов. 
Пользователям сайта также доступен сервис «Список покупок». 
Он позволяет создавать список продуктов, которые нужно купить для приготовления 
выбранных блюд.

## Технологии
- Python
- Docker
- PostgreSQL
- Django REST framework
- Gunicorn
- Nginx
- React

💡[Сылка на потыкать](https://thebestfoodgram.ddns.net/)

## Необходимо для запуска
💡[Docker](https://docs.docker.com/engine/install/)

## Запуск проекта локально

Клонировать репозиторий:
```shell
git clone https://github.com/IvanZabelin/foodgram.git
```

Перейти в каталог проекта:
```shell
cd foodgram
```

Создать .env:
```shell
touch .env
```

Шаблон содержимого для .env файла:
```shell
# Django settings
DEBUG=False
SECRET_KEY=<django_secret_key>
ALLOWED_HOSTS=127.0.0.1;localhost;<example.com;xxx.xxx.xxx.xxx>

# DB
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432

# Superuser
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@admin.com
ADMIN_PASSWORD=admin
```

Развернуть приложение:
```shell
docker compose -f docker-compose.dev.yml up -d
```
В процессе развертывания приложения запускается скрипт `backend/up.sh`.
- Собирает статику и копирует в volume.
- Выполняет миграции.
- Создает суперпользователя.
- Создает теги.
- Запускает сервер gunicorn.

Выполнить заполнение базы ингредиентами:
```shell
docker compose exec backend python manage.py load_data_csv
```

После успешного запуска, проект доступен на локальном IP `127.0.0.1:8080`.

## Запуск проекта на удаленном сервере

💡 Инструкция предполагает, что удаленный сервер настроен на работу по SSH. 
На сервере установлен Docker. 
Установлен и настроен nginx в качестве балансировщика нагрузки.
Для развертывания на удаленном сервере необходимо клонировать репозиторий на 
локальную машину. Подготовить и загрузить образы на Docker Hub.

Клонировать репозиторий:
```shell
git clone git clone <https or SSH URL>
```

Перейти в каталог проекта:
```shell
cd foodgram
```

Создать .env:
```shell
touch .env
```

Шаблон содержимого для .env файла:
```shell
# Django settings
DEBUG=False
SECRET_KEY=<django_secret_key>
ALLOWED_HOSTS=127.0.0.1;localhost;<example.com;xxx.xxx.xxx.xxx>

# DB
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432

# Docker images
BACKEND_IMAGE=<username>/food_back
FRONTEND_IMAGE=<username>/food_front
GATEWAY_IMAGE=<username>/food_gateway

# Superuser
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@admin.com
ADMIN_PASSWORD=admin
```

Создать docker images образы:
```shell
sudo docker build -t <username>/food_back backend/foodgram
sudo docker build -t <username>/food_front frontend/
sudo docker build -t <username>/food_gateway gateway/
```

Загрузить образы на Docker Hub:
```shell
sudo docker push <username>/food_back
sudo docker push <username>/food_front
sudo docker push <username>/food_gateway
```

Создать на сервере папку `foodgram` 
```shell
mkdir /home/<user name>/foodgram
```

Перенести на удаленный сервер файлы`.env` и `docker-compose.production.yml`.
```shell
scp .env docker-compose.prod.yml <user@server-address>:/home/<user name>/foodgram
```

Подключиться к серверу:
```shell
ssh user@server-address
```

Перейти в директорию `foodgram`:
```shell
cd /home/<user name>/foodgram
```

Выполнить сборку приложений:
```shell
sudo docker compose -f docker-compose.production.yml up -d
```

Выполнить заполнение базы ингредиентами:
```shell
docker compose -f docker-compose.production.yml exec backend python manage.py load_data_csv
```

## GitHub Actions
Для использования автоматизированного развертывания и тестирования нужно 
изменить `.github/workflows/main.yml` под свои параметры и задать Actions secrets
в репозитории.

Actions secrets:
- `secrets.DOCKER_USERNAME`
- `secrets.DOCKER_PASSWORD`
- `secrets.HOST`
- `secrets.USER`
- `secrets.SSH_KEY`
- `secrets.SSH_PASSPHRASE`
- `secrets.TELEGRAM_TO`
- `secrets.TELEGRAM_TOKEN`
