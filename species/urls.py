from django.urls import path

from .views import app_content_db, TagsList, PortraitDetail, SimpleTagsList, SpeciesList, \
    AppContentCharacterValue, species

urlpatterns = [
    path('species/', SpeciesList.as_view()),
    path('species/<int:id>/', species),
    path('species/portrait/', PortraitDetail.as_view()),
    path('tags/filter/', TagsList.as_view()),
    path("app-content/db/", app_content_db, name="app-content-db"),
    path("app-content/character-values/", AppContentCharacterValue.as_view()),
    path("tags/", SimpleTagsList.as_view()),
]
