# naturblick-django

This is the CMS for naturblick. We use WSGI/Gunicorn.

## Setup for local development

* once: `sudo pip install virtualenv`
* `cd naturblick-django`
* `virtualenv env`
* `source env/bin/activate` 

## Adding new requirements and example commands

* `pip freeze > requirements.txt`
* `docker compose exec naturblick-django python manage.py migrate`
* `docker-compose exec naturblick-django python manage.py createsuperuser
