# naturblick-django

This is the CMS for naturblick. We use WSGI/Gunicorn.

## Shortcut for existing environment:
```
export DJANGO_ENV="development"
export DJANGO_POSTGRES="species"
export DJANGO_POSTGRES_USER="naturblick"
export DJANGO_POSTGRES_PASSWORD="CxxOKzBllAQPnt1qgldN"
source env/bin/activate
```


## Some sample dev tasks and corresponding commands

* changing models: `python manage.py makemigrations` -> `python manage.py migrate`
* changing dependencies `pip freeze > requirements.txt`
* create superuser `python manage.py createsuperuser`
* Execute command in production `docker compose exec django python manage.py COMMAND`
* running tests `python manage.py test species`


## Setup for local development

* once: `sudo pip install virtualenv`
* Set up all required envs:
```
export DJANGO_ENV="development"
export DJANGO_POSTGRES="species"
export DJANGO_POSTGRES_USER="naturblick"
export DJANGO_POSTGRES_PASSWORD="CxxOKzBllAQPnt1qgldN"
```
* Start developement DB `docker compose -f resources/docker-compose.yaml up -d` with or without `resources/pg_dump.sql` 
* `virtualenv env`
* `source env/bin/activate` 
* `pip install --no-cache-dir -r requirements.txt`
* `python manage.py migrate`
* If no dump was used: `python manage.py createsuperuser`
* `python manage.py runserver`

## Start over
'''
docker compose -f resources/docker-compose.yaml down
rm -r env
'''

## Creating a new django-db container and prepare for replication

WAL-Level is already set in docker-compose. Just execute 

```
\set pass `echo "$REP_USER_PASS"`
CREATE USER repuser WITH REPLICATION PASSWORD :'pass' LOGIN;
```

```
GRANT SELECT ON species TO repuser;
GRANT SELECT ON "group" TO repuser;
CREATE PUBLICATION species_publication FOR TABLE species, "group";
```

and the DB is ready for replication.
