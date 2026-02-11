python manage.py migrate
python manage.py collectstatic --noinput --clear
python manage.py compilemessages

gunicorn --config gunicorn_config.py
