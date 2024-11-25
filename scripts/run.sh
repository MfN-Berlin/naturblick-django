python manage.py migrate
python manage.py collectstatic --noinput

gunicorn --config gunicorn_config.py