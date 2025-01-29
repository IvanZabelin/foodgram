FROM python:3.9-slim-buster

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# Копируем все файлы
COPY . .

# Делаем up.sh исполнимым
RUN chmod +x /app/up.sh
