from django.urls import path
from .views import SpeciesList, app_content, TagsList

urlpatterns = [
    path('', SpeciesList.as_view()),
    path('tags/', TagsList.as_view()),
    # path("<int:species_id>/", SpeciesDetail.as_view()),
    path("app-content/", app_content, name="app-content"),
]