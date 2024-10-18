import os

env = os.getenv('DJANGO_ENV', 'production')

if env == 'production':
    from .prodsettings import *
else:
    from .devsettings import *