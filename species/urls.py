from django.urls import path
from django.urls import re_path

from .views import app_content_db, app_content_leicht_db, app_content_leicht_image_list, \
    TagsList, PortraitDetail, SimpleTagsList, SpeciesList, AppContentCharacterValue, \
    species, specgram, species_list, GroupsList

urlpatterns = [
    path('species/filter/', SpeciesList.as_view(), name="species-filter"),
    path('species/', species_list, name="species-list"),
    path('species/<int:id>/', species, name="species"),
    path('species/portrait/', PortraitDetail.as_view(), name="portrait-detail"),
    re_path(r'^specgram/(?P<filename>.+\.mp3\.png)$', specgram),
    path('tags/filter/', TagsList.as_view(), name="tags-filter"),
    path("app-content/db/", app_content_db, name="app-content-db"),
    path("app-content/leicht-db/", app_content_leicht_db,
         name="app-content-leicht-db"),
    path("app-content/leicht-image-list/", app_content_leicht_image_list,
         name="app-content-leicht-image-list"),
    path("app-content/character-values/", AppContentCharacterValue.as_view()),
    path("tags/", SimpleTagsList.as_view(), name="tags"),
    path("groups/", GroupsList.as_view(), name="groups")
]
