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
* running tests `python manage.py test species`

## settings up database

1.) Get data from existing Strapi-DB

```
docker exec strapi-db pg_dump -U strapi -t 'species*|faunaportraits*|floraportrai^C*|components_species\*|upload_file\*' --schema-only strapi | sed s'/public./strapi\_/g' | sed '/^SET/d' | sed '/^SELECT pg\_catalog.set/d' | sed '/^--/d' | sed '/._OWNED._/d' | sed '/._OWNER._/d' | sed '/^ALTER TABLE ONLY._regclass);/d' | sed '/^GRANT SELECT._/d' | awk '!/CREATE SEQUENCE/ && !p {print} /CREATE SEQUENCE/ {p=1} /;/ {p=0}' | sed 's/strapi\_components\_speciesportrait\_species\_portrait\_images\_components/strapi\_components\_speciesportrait\_species\_portrait\_images\_compo/g' | sed 's/species\_pkey/strapi\_species_pkey/g' | sed '/^$/d' > schema.sql\
```

```
docker exec strapi-db pg_dump -U strapi -t 'species*|faunaportraits*|floraportrait*|components_species*|upload_file*' --column-inserts --data-only strapi | sed s'/public\./strapi_/g' | sed '/^SET/d' | sed '/^SELECT pg_catalog\.set/d' | sed '/^--/d' | sed '/.*OWNED.*/d' | sed '/.*OWNER.*/d' | sed '/^ALTER TABLE ONLY.*regclass);/d' | sed '/^GRANT SELECT.*/d' | awk '!/CREATE SEQUENCE/ && !p {print} /CREATE SEQUENCE/ {p=1} /;/ {p=0}' | sed 's/strapi_components_speciesportrait_species_portrait_images_components/strapi_components_speciesportrait_species_portrait_images_compo/g' | sed 's/species_pkey/strapi_species_pkey/g' | sed '/^$/d' > data.sql
```

2.) Prepare empty django-db and execute migrations

```
python manage.py makemigrations && python manage.py migrate && python manage.py loaddata groups && python manage.py createsuperuser 
```

3.) Copy dumps to django-db and execute it

```
docker cp data.sql django-db:/ && docker cp schema.sql django-db:/ && docker exec django-db psql -U naturblick species -f /schema.sql && docker exec django-db psql -U naturblick species -f /data.sql
```

4.) Copy init.sql to django db and execute it

```
docker cp init.sql django-db:/ docker exec django-db psql -U naturblick species -f /init.sql
```

5.) copy strapi-upload images to `media-root/portrait_images` (only needed ones)