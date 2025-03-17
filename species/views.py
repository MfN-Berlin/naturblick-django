from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Species, CharacterValue
from .serializers import SpeciesSerializer, CharacterValueSerializer
from .utils import create_sqlite_file


def app_content(request):
    """Django view that generates and serves an SQLite file."""

    sqlite_db = create_sqlite_file()

    response = FileResponse(open(sqlite_db, "rb"), as_attachment=True)
    response["Content-Disposition"] = f'attachment; filename="species-db.sqlite3"'

    return response


class SpeciesList(generics.ListAPIView):
    # queryset = Species.objects.all()

    def get_queryset(self):
        queryset = Species.objects.all()
        lang_filter = self.request.query_params.get('language')

        if lang_filter:
            queryset = queryset.filter(language=lang_filter)

        return queryset

    serializer_class = SpeciesSerializer


class SpeciesDetail(APIView):
    def get(self, request, species_id):
        species = get_object_or_404(Species, id=species_id)
        serializer = SpeciesSerializer(species)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CharacterValues(generics.ListAPIView):
    queryset = CharacterValue.objects.order_by('id').all()
    serializer_class = CharacterValueSerializer
