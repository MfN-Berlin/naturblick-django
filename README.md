# naturblick-django

This is the CMS for naturblick. We use WSGI/Gunicorn.

## Creating a new django-db container (prepare for replication)

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

## Setup for local development

### postgres database

* `export DJANGO_ENV="development"`
* `export DJANGO_POSTGRES_PASSWORD="..."`
* `export DJANGO_POSTGRES_USER="..."`
* `export DJANGO_POSTGRES="..."`
* copy `pg_dump.sql` into `/resources` folder
* copy all media to local system: `rsync -a worker:/local/naturblick/django/media/* media-root/`
* start or restart fresh: `docker compose down && docker compose up -d`

### Django 

* once: `sudo pip install virtualenv`
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

## setting up database

1.) Get data from existing Strapi-DB

```
docker exec strapi-db pg_dump -U strapi -t 'species*|faunaportraits*|floraportrait*|components_species*|upload_file*|tags*|species__tags*|characters*|character_values*|sources_impressum*|sources_translations*' --schema-only strapi | sed s'/public./strapi\_/g' | sed '/^SET/d' | sed '/^SELECT pg\_catalog.set/d' | sed '/^--/d' | sed '/._OWNED._/d' | sed '/._OWNER._/d' | sed '/^ALTER TABLE ONLY._regclass);/d' | sed '/^GRANT SELECT._/d' | awk '!/CREATE SEQUENCE/ && !p {print} /CREATE SEQUENCE/ {p=1} /;/ {p=0}' | sed 's/strapi\_components\_speciesportrait\_species\_portrait\_images\_components/strapi\_components\_speciesportrait\_species\_portrait\_images\_compo/g' | sed 's/species\_pkey/strapi\_species_pkey/g' | sed '/^$/d' | sed '/.*OWNER TO strapi;/d' | sed '/^ALTER SEQUENCE.*/d' | sed '/^ALTER TABLE ONLY.*/d' > schema.sql
```

```
docker exec strapi-db pg_dump -U strapi -t 'species*|faunaportraits*|floraportrait*|components_species*|upload_file*|tags*|species__tags*|characters*|character_values*|sources_impressum*|sources_translations*' --column-inserts --data-only strapi | sed s'/public\./strapi_/g' | sed '/^SET/d' | sed '/^SELECT pg_catalog\.set/d' | sed '/^--/d' | sed '/.*OWNED.*/d' | sed '/.*OWNER.*/d' | sed '/^ALTER TABLE ONLY.*regclass);/d' | sed '/^GRANT SELECT.*/d' | awk '!/CREATE SEQUENCE/ && !p {print} /CREATE SEQUENCE/ {p=1} /;/ {p=0}' | sed 's/strapi_components_speciesportrait_species_portrait_images_components/strapi_components_speciesportrait_species_portrait_images_compo/g' | sed 's/species_pkey/strapi_species_pkey/g' | sed '/.*OWNER TO strapi;/d' | sed '/^ALTER SEQUENCE.*/d' > data.sql
```

2.) Prepare empty django-db and execute migrations

```
python manage.py migrate && python manage.py loaddata groups 
```

3.) Copy dumps to django-db and execute it

```
docker cp data.sql django-db:/ && docker cp schema.sql django-db:/ && docker exec django-db psql -U naturblick species -f /schema.sql && docker exec django-db psql -U naturblick species -f /data.sql
```

4.) Copy init.sql to django db and execute it

```
docker cp init.sql django-db:/ && docker exec django-db psql -U naturblick species -f /init.sql
```

## Copy media files into directories

base directory is `/app/media-root/`

# avatar_images, portrait_images, audio_files, spectrogram_images, character_images

Directories should already be created.

```
SRC_DIR=xx  # strapi upload
DEST_DIR=yy # django media
docker exec django-db psql -U naturblick species -c "select 'scp $SRC_DIR/' || substr(image, 15) || ' $DEST_DIR/avatar_images' from avatar;" | tail -n+3 | head -n-2 >> copy_files.sh

docker exec django-db psql -U naturblick species -c "select 'scp $SRC_DIR/' || substr(image, 17) || ' $DEST_DIR/portrait_images' from portrait_image_file;" | tail -n+3 | head -n-2 >> copy_files.sh

docker exec django-db psql -U naturblick species -c "select 'scp $SRC_DIR/' || substr(audio_file,13) || ' $DEST_DIR/audio_files'  from faunaportrait_audio_file;" | tail -n+3 | head -n-2 >> copy_files.sh

docker exec django-db psql -U naturblick species -c "select 'scp $SRC_DIR/' || substr(audio_spectrogram,20) || ' $DEST_DIR/spectrogram_images' from faunaportrait_audio_file;" | tail -n+3 | head -n-2 >> copy_files.sh

docker exec django-db psql -U naturblick species -c "select 'scp $SRC_DIR/' || substr(image,18) || ' $DEST_DIR/character_images' from character_value where image is not null;" | tail -n+3 | head -n-2 >> copy_files.sh
```

**trigger management command:**

```
python manage.py generateimages
```
