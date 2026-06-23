from django.urls import path

from .views import app_content_db, app_content_leicht_db, app_content_leicht_image_list, \
    AppContentCharacterValue, GroupsList, VolunteerImages

urlpatterns = [
    path("app-content/db/", app_content_db, name="app-content-db"),
    path("app-content/leicht-db/", app_content_leicht_db, name="app-content-leicht-db"),
    path("app-content/leicht-image-list/", app_content_leicht_image_list, name="app-content-leicht-image-list"),
    path("app-content/character-values/", AppContentCharacterValue.as_view()),
    path("app-content/groups/", GroupsList.as_view(), name="groups"),
    path('species/volunteerimages/', VolunteerImages.as_view(), name="volunteer-images"),
]
