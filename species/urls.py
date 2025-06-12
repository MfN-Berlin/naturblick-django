from django.urls import path
from django.urls import re_path

from .views import app_content_db, TagsList, PortraitDetail, SimpleTagsList, SpeciesList, \
    AppContentCharacterValue, species, specgram, species_list, PlantnetPowoidMappingList

urlpatterns = [
    path('species/filter/', SpeciesList.as_view()),
    path('species/', species_list),
    path('species/<int:id>/', species),
    path('species/portrait/', PortraitDetail.as_view()),
    re_path(r'^specgram/(?P<filename>.+\.mp3\.png)$', specgram),
    path('tags/filter/', TagsList.as_view()),
    path("app-content/db/", app_content_db, name="app-content-db"),
    path("app-content/character-values/", AppContentCharacterValue.as_view()),
    path("tags/", SimpleTagsList.as_view()),
    path("plantnet-species-mappings/", PlantnetPowoidMappingList.as_view())
]
