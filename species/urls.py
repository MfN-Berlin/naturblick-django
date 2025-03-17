from django.urls import path
from .views import app_content, TagsList, PortraitDetail, SimpleTagsList, SpeciesList

urlpatterns = [
    path('species/', SpeciesList.as_view()),
    path('species/portrait/', PortraitDetail.as_view()),
    path('tags/filter/', TagsList.as_view()),
    # path("<int:species_id>/", SpeciesDetail.as_view()),
    path("app-content/", app_content, name="app-content"),
    path("tags/", SimpleTagsList.as_view()),
]