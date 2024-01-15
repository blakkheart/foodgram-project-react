# Веб-приложение Foodgram 

## Описание
Веб-приложение представляет собой проект с несколькими страницами: главной, страницей рецепта, страницей пользователя, страницей подписок, избранным, списком покупок, а также страницей создания и редактирования рецепта. Главная страница содержит рецепты, отсортированные по дате публикации, с возможностью постраничной пагинации. 

Страница рецепта предоставляет полное описание рецепта, позволяя авторизованным пользователям добавлять рецепты в избранное и в список покупок, а также подписываться на автора. Страница пользователя отображает имя пользователя, все его опубликованные рецепты. 

Страница подписок доступна только владельцу аккаунта, позволяя просматривать рецепты от подписанных авторов.  

Избранное позволяет авторизованным пользователям отмечать рецепты и просматривать свой список избранных. Список покупок, доступный только авторизованным пользователям, позволяет добавлять репецты в корзину и скачивать список в формате pdf, где ингредиенты не дублируются. 

Создание и редактирование рецепта доступны только авторизованным пользователям, с обязательным заполнением всех полей. Фильтрация по тегам позволяет классифицировать и искать рецепты. 

## Технологии

- Фронтенд: React
- Бэкенд: Django Rest Framework
- База данных: PostgreSQL
- Nginx
- Docker
- Gunicorn
- Github actions

## Запуск проекта

Проект разделен на три контейнера: nginx, PostgreSQL и Django, запускаемые через docker-compose. Файлы для сборки фронтенда хранятся в репозитории foodgram-project-react в папке frontend.

Для запуска проекта выполните следующие шаги:
1. Склонируйте репозиторий foodgram-project-react на свой компьютер.
2. Создайте и активируйте виртуальное окружение:
   - Windows
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```
   - Linux/macOS
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Обновите [pip](https://pip.pypa.io/en/stable/):
   - Windows
   ```bash
   (venv) python -m pip install --upgrade pip
   ```
   - Linux/macOS
   ```bash
   (venv) python3 -m pip install --upgrade pip
   ```
4. Установите зависимости из файла requirements.txt:
   ```bash
   (venv) pip install -r requirements.txt
   ```
5. Создайте и заполните файл .env по примеру с файлом .env.example.
6. Запустите проект в трёх контейнерах с помощью Docker Compose:
   ```bash
    docker compose up
   ```
7. Сделайте миграцию:
   ```bash
    docker compose exec backend python manage.py migrate
   ```
8. Соберите статику:
    ```bash
    docker compose exec backend python manage.py collectstatic
    ```
    ```bash
    docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
    ```
9. Загрузите данные с ингредиентами:
   ```bash
    docker compose exec backend python manage.py import_ingredients
   ```
10. Если потребуется работа в панели администратора, создайте суперпользователя:
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```
 
## Демо
Проект развернут на домашнем сервере и доступен по адресу [foodgram.myftp.biz](foodgram.myftp.biz)
 
## Автор
- [@blakkheart](https://github.com/blakkheart) 
