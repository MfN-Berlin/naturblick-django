import os

env = os.getenv('DJANGO_ENV', 'production')

if env == 'production':
    workers = 4
    loglevel = 'info'
    #accesslog = '/var/log/gunicorn/access.log'
    #errorlog = '/var/log/gunicorn/error.log'
    timeout = 120
else:
    workers = 1
    loglevel = 'debug'
    reload = True

bind = '0.0.0.0:8000'
wsgi_app = 'naturblick.wsgi:application'