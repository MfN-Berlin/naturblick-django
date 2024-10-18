from django.urls import include, path
from .views import SpeciesList

urlpatterns = [
    path('', SpeciesList.as_view())
]