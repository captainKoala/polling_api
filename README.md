# API Polling

API для проведения опросов пользователей

## Разворачиваиние приложения

1. Поместите в подкаталог polling файл .env с переменными окружения следующего 
содержания (*измените секретный ключ и пароль для базы данных*):
```
SECRET_KEY=addHereYourOwnSecretKey
POSTGRES_PASSWORD=itIsYourDatabasePassword
POSTGRES_DB=polling
POSTGRES_USER=polling
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=backend 127.0.0.1 localhost
```
2. Из корневой директории с проектом выполните:

```docker-compose up -d --build```

3. Выполните миграции:

```docker-compose exec backend python manage.py migrate```

3. Для сборки статических файлов выполните:

```docker-compose exec backend python manage.py collectstatic --no-input```

6. Создание суперпользователя (необходимо указать имя пользователя, email, 
пароль для входа)

```docker-compose exec backend python manage.py createsuperuser```

7. Проект доступен по адресу http://127.0.0.1/ , корень API - 
http://127.0.0.1/api/ , панель администратора - http://127.0.0.1/admin/

## Создание пользователей

Создание пользователей доступно администраторам (в том числе суперпользователю)
в [панели администратора](http://127.0.0.1/admin/). Для создания пользователей 
с правами администратора необходимо отметить флажок "Статус персонала".

## Документация

Документация по API будет доступна по адресу http://127.0.0.1/redoc/ .
