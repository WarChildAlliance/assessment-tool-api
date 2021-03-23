# Assessment tool API

## Django Documentation

## Run project

    docker-compose up --build

### Install new packages

    docker-compose run --rm web pipenv install <package-name>

### Add new app

    docker-compose run --rm web python manage.py startapp <app-name>

### Create migrations files

    docker-compose run --rm web python manage.py makemigrations

### Apply migrations

    docker-compose run --rm web python manage.py migrate

### Create superuser

    docker-compose run --rm web python manage.py createsuperuser

### Run tests

    docker-compose run --rm web python manage.py test

### Generate static files

    docker-compose run --rm web python manage.py collectstatic

### Load languages and countries

    docker-compose run --rm web python manage.py loadlanguagescountries