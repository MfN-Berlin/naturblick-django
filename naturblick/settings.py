import os

env = os.getenv("DJANGO_ENV")

match env:
    case "production":
        from .prodsettings import *
    case "development":
        from .devsettings import *
    case _:
        raise Exception("Missing environment variable DJANGO_ENV")
