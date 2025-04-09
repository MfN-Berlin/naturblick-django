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

## setting up database

1.) Get data from existing Strapi-DB

```
docker exec strapi-db pg_dump -U strapi -t 'species*|faunaportraits*|floraportrait*|components_species*|upload_file*|tags*|species__tags*|characters*|character_values*|sources_impressum*|sources_translations*' --schema-only strapi | sed s'/public./strapi\_/g' | sed '/^SET/d' | sed '/^SELECT pg\_catalog.set/d' | sed '/^--/d' | sed '/._OWNED._/d' | sed '/._OWNER._/d' | sed '/^ALTER TABLE ONLY._regclass);/d' | sed '/^GRANT SELECT._/d' | awk '!/CREATE SEQUENCE/ && !p {print} /CREATE SEQUENCE/ {p=1} /;/ {p=0}' | sed 's/strapi\_components\_speciesportrait\_species\_portrait\_images\_components/strapi\_components\_speciesportrait\_species\_portrait\_images\_compo/g' | sed 's/species\_pkey/strapi\_species_pkey/g' | sed '/^$/d' > schema.sql
```

```
docker exec strapi-db pg_dump -U strapi -t 'species*|faunaportraits*|floraportrait*|components_species*|upload_file*|tags*|species__tags*|characters*|character_values*|sources_impressum*|sources_translations*' --column-inserts --data-only strapi | sed s'/public\./strapi_/g' | sed '/^SET/d' | sed '/^SELECT pg_catalog\.set/d' | sed '/^--/d' | sed '/.*OWNED.*/d' | sed '/.*OWNER.*/d' | sed '/^ALTER TABLE ONLY.*regclass);/d' | sed '/^GRANT SELECT.*/d' | awk '!/CREATE SEQUENCE/ && !p {print} /CREATE SEQUENCE/ {p=1} /;/ {p=0}' | sed 's/strapi_components_speciesportrait_species_portrait_images_components/strapi_components_speciesportrait_species_portrait_images_compo/g' | sed 's/species_pkey/strapi_species_pkey/g' > data.sql
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

### avatar_images, portrait_images, audio_files, spectrogram_images, character_images

Directories should already be created.

```
UPLOAD_LOCATION=xx
docker exec django-db psql -U naturblick species -c "select 'scp $UPLOAD_LOCATION/' || substr(image, 15) || ' avatar_images' from avatar;" | tail -n+3 | head -n-2 >> copy_files.sh

docker exec django-db psql -U naturblick species -c "select 'scp $UPLOAD_LOCATION/' || substr(image, 17) || ' portrait_images' from portrait_image_file;" | tail -n+3 | head -n-2 >> copy_files.sh

docker exec django-db psql -U naturblick species -c "select 'scp $UPLOAD_LOCATION/' || substr(audio_file,13) || ' audio_files'  from faunaportrait_audio_file;" | tail -n+3 | head -n-2 >> copy_files.sh

docker exec django-db psql -U naturblick species -c "select 'scp $UPLOAD_LOCATION/' || substr(audio_spectrogram,20) || ' spectrogram_images' from faunaportrait_audio_file;" | tail -n+3 | head -n-2 >> copy_files.sh

docker exec django-db psql -U naturblick species -c "select 'scp $UPLOAD_LOCATION/' || substr(image,18) || ' character_images' from character_value where image is not null;" | tail -n+3 | head -n-2 >> copy_files.sh
```

**trigger management command:**

```
python manage.py generateimages
```
