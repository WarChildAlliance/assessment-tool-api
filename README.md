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

*Tip : Use* `--keepdb` *optional parameter at the end in order to use the same test database accross all tests*

### Generate static files

    docker-compose run --rm web python manage.py collectstatic

### Load fixtures data

    docker-compose run --rm web python loaddata <fixture>

    examples :
    - docker-compose run --rm web python loaddata users
    - docker-compose run --rm web python loaddata assessments

*Be careful with the order*