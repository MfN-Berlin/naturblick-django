from .models import Species, CharacterValue
from rest_framework import generics
from .serializers import SpeciesSerializer, SpeciesDetailSerializer, CharacterValueSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from django.http import FileResponse
from .utils import create_sqlite_file


def app_content(request):
    """Django view that generates and serves an SQLite file."""

    sqlite_db = create_sqlite_file()

    response = FileResponse(open(sqlite_db, "rb"), as_attachment=True)
    response["Content-Disposition"] = f'attachment; filename="species-db.sqlite3"'

    return response

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
    queryset = CharacterValue.objects.order_by('id').all()
    serializer_class = CharacterValueSerializer