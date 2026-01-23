python manage.py migrate
python manage.py collectstatic --noinput --clear

gunicorn --config gunicorn_config.py
