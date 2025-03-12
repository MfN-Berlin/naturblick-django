from django.urls import path
from .views import SpeciesList, SpeciesDetail, app_content

urlpatterns = [
    path('', SpeciesList.as_view()),
    path("<int:species_id>/", SpeciesDetail.as_view()),
    path("app-content/", app_content, name="app-content"),
]