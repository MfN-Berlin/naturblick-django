from django.urls import path
from .views import SpeciesList, SpeciesDetail

urlpatterns = [
    path('', SpeciesList.as_view()),
    path("<int:species_id>/", SpeciesDetail.as_view()),
]