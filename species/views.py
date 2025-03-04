from .models import Species, CharacterValue
from rest_framework import generics
from .serializers import SpeciesSerializer, SpeciesDetailSerializer, CharacterValueSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404



class SpeciesList(generics.ListAPIView):
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer

#def detail(request, species_id):
#    try:
#        species = Species.objects.get(pk=species_id)
#    except Species.DoesNotExist:
#        raise Http404("Species does not exist")
#    serializer = SpeciesDetailSerializer(species)
#    return Response(serializer.data, status=status.HTTP_200_OK)


class SpeciesDetail(APIView):
    def get(self, request, species_id):
        species = get_object_or_404(Species, id=species_id)
        serializer = SpeciesDetailSerializer(species)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CharacterValues(generics.ListAPIView):
    queryset = CharacterValue.objects.order_by('character').all()
    serializer_class = CharacterValueSerializer