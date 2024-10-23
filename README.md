# naturblick-django

This is the CMS for naturblick. We use WSGI/Gunicorn.

## Setup for local development

* once: `sudo pip install virtualenv`
* `export DJANGO_ENV="development"`
* `cd naturblick-django`
* `virtualenv env`
* `source env/bin/activate` 
* `cd naturblick` and `pip install --no-cache-dir -r requirements.txt`
* `python manage.py migrate`
* `python manage.py runserver`

## Some sample dev tasks and corresponding commands

* changing models: `python manage.py makemigrations` -> `python manage.py migrate`
* changing dependencies `pip freeze > requirements.txt`
* create superuser `python manage.py createsuperuser`
* Execute command in production `docker compose exec django python manage.py COMMAND`

