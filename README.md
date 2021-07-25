# Описание
Проект Foodgram - сервис который позволяет постить рецепты, подписываться на авторов и скачивать списки продуктов.

# Установка проекта 
1. Скопируйте проект к себе на компютер: ```git clone https://github.com/nist2902/foodgram-project-react```
2. Склонируйте репозиторий. В корневой директории создайте файл .env со значениями:  
```DB_ENGINE=django.db.backends.postgresql``` 
```DB_NAME=postgres``` 
```POSTGRES_USER=postgres``` 
```POSTGRES_PASSWORD=postgres```   # ваш пароль 
```DB_HOST=db``` 
```DB_PORT=5432```
3. Запустите Docker: ```sudo docker-compose up``` 
4. Выполните миграции внутри докера: ```sudo docker-compose exec web python manage.py migrate --noinput``` 
5. Создайте суперпользователя внутри докера: ```sudo docker-compose exec web python manage.py createsuperuser``` 
6. Соберите статику внутри докера: ```sudo docker-compose exec web python manage.py collectstatic --no-input``` 

# Workflow checker 
![Checker workflow](https://github.com/nist2902/foodgram-project-react/actions/workflows/main.yml/badge.svg) 

# Адрес на сервере 
http://foodgrampraktikum.ml/

# Данные для входа в админ-панель:
Адрес: http://foodgrampraktikum.ml/admin
Mail: admin@admin.com
Пароль: admin
