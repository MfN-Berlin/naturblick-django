from django.shortcuts import render
from .models import Species
from rest_framework import generics
from .serializers import SpeciesSerializer

class SpeciesList(generics.ListAPIView):
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer