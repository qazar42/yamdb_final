### Цель проекта:

Проект YaMDb собирает отзывы пользователей на произведения.
Произведения делятся на категории: «tc1», «tc2"
Список категорий может быть расширен администратором.

![yamdb_workflow](https://github.com/qazar42/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

### Как запустить проект:

```
git clone git@github.com:qazar42/yamdb_final.git
```
```
cd api_yamdb/infra
```
```
sudo docker-compose up -d --build
```
```
sudo docker-compose exec web python manage.py migrate
```
```
sudo docker-compose exec web python manage.py createsuperuser
```
```
sudo docker-compose exec web python manage.py collectstatic --no-input 
```
```
sudo docker-compose exec web python manage.py loaddata fixtures.json
```

### API examples:

```
#Получить токен
POST  http://127.0.0.1/api/v1/auth/token/
Content-Type: application/json 
 
{ 
    "username": "username", 
    "password": "password" ,
    "confirmation_code":"confirmation_code"
} 
```
```
#Получить произведения
GET http://127.0.0.1/api/v1/titles/
```
```
#Получить произведения по фильтру жанра
GET http://127.0.0.1/api/v1/titles/?genre=example
```
```
#Получить произведения по фильтру категории
GET http://127.0.0.1/api/v1/titles/?category=example
```
```
#Получить произведения по фильтру год
GET http://127.0.0.1/api/v1/titles/?year=example
```
```
#Получить произведения по фильтру имя
GET http://127.0.0.1/api/v1/titles/?name=example
```
```
#Опубликовать произведения
POST http://127.0.0.1/api/v1/titles/
Content-Type: application/json
Authorization: Bearer example_token

{
    "name":"example",
    "year":"example",
    "category": "example",
    "genre": ["example"]
}
```
```
### Создать категорию
POST http://127.0.0.1/api/v1/categories/
Content-Type: application/json
Authorization: Bearer example_token

{
    "name":"example",
    "slug":"example"

}
```
```
# Получить категории
GET http://127.0.0.1/api/v1/categories/
```
```
#Создать жанр
POST http://127.0.0.1/api/v1/genres/
Content-Type: application/json
Authorization: Bearer example_token

{
    "name":"example",
    "slug":"example"

}
```
```
#Получить жанры
GET http://127.0.0.1/api/v1/genres/
```
Более подробную информацию о реализованных методах можно получить после запуска проекта по ссылке в браузере http://127.0.0.1/redoc/

### Enviroments
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
```
```
DB_NAME= #имя базы данных
```
```
POSTGRES_USER= # логин для подключения к базе данных
```
```
POSTGRES_PASSWORD= # пароль для подключения к БД 
(установите свой)
```
```
DB_HOST= # название сервиса (контейнера)
```
```
DB_PORT= # порт для подключения к БД 
```

### Authors
@KostromDan
@qazar42
@ilonka05


### License

MIT