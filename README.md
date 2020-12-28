# foodgram-project


## 
Простой и удобный сайт для рецептов

При разработке приложения использованы фреймфорки ```django```. В качестве базы выступает ```postgresql```
Запуск проекта осуществляется средствами ```docker```

## Установка
Предварительно в директории foodgram должен быть добавлен файл .env с таким содержимым:

DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД

#### 1. Установка docker и docker-compose

Если у вас уже установлены docker и docker-compose, этот шаг можно пропустить, иначе можно воспользоваться официальной [инструкцией](https://docs.docker.com/engine/install/).

#### 2. Запуск контейнера
```bash
docker-compose up
```
### 3. Выключение контейнера
```bash
docker-compose down
```


## Использование
#### Создание суперпользователя Django
```bash
docker-compose run web python manage.py createsuperuser
```

## Основные использованные технологии
* python 3.8
* [django](https://www.djangoproject.com/)
* [posgresql](https://www.postgresql.org/)
* [docker](https://www.docker.com/)
