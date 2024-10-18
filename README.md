# naturblick-django

This is the CMS for naturblick. We use WSGI/Gunicorn.

## Setup for local development

* once: `sudo pip install virtualenv` and clone repo
* export environment variables: DJANGO_POSTGRES_PASSWORD, DJANGO_ENV, DJANGO_POSTGRES_DATA, DJANGO_POSTGRES, DJANGO_POSTGRES_USER
* `cd naturblick-django`
* `virtualenv env`
* `source env/bin/activate` 
* `cd naturblick` and `python manage.py runserver`

## Adding new requirements and example commands

* `pip freeze > requirements.txt`
* `docker compose exec django python manage.py migrate`
* `docker compose exec django python manage.py createsuperuser
