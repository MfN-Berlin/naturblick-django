from django.db.models import Q
from django.http import FileResponse
from rest_framework import generics

from .models import Species, Tag
from .serializers import SpeciesSerializer, TagSerializer
from .utils import create_sqlite_file


def app_content(request):
    """Django view that generates and serves an SQLite file."""

    sqlite_db = create_sqlite_file()

    response = FileResponse(open(sqlite_db, "rb"), as_attachment=True)
    response["Content-Disposition"] = f'attachment; filename="species-db.sqlite3"'

    return response


#
# all requests from platform
#

# 1.)
# StrapiSpeciesFilter
#   species/filter?lang=de&query=&_limit=30
#   {"count":"690",
#   "data":[{"id":1,"speciesid":"amphibian_0de18656","localname":"Teichmolch","group":"amphibian","sciname":"Lissotriton vulgaris","synonym":null,"url":"/uploads/crop_d60f7f6c98b0fcf1aa52e7b0_f0b5f2e568.jpg","imageOwner":"Piet Spaans Viridiflavus","imageLicense":"CC BY-SA 2.5","imageSource":"https://commons.wikimedia.org/wiki/File:LissotritonVulgarisMaleWater.JPG"}, ...

# 2.)
#   tags/filter?lang=de&tagsearch=&_limit=-1
#   [{"tag_id":98,"localname":"Ameisenausbreitung"}, {"tag_id":39,"localname":"Amphibie"}, ...

class TagsList(generics.ListAPIView):

    def get_queryset(self):
        queryset = Tag.objects.all()
        query = self.request.query_params.get('tagsearch')
        lang = self.request.query_params.get('lang')

        if query:
            if lang and lang == 'de':
                queryset = queryset.filter(Q(name__icontains=query))
            elif lang and lang == 'en':
                queryset = queryset.filter(Q(english_name__icontains=query))
            else:
                queryset = queryset.filter(Q(name__icontains=query) | Q(english_name__icontains=query))

        return queryset

    serializer_class = TagSerializer


# 3.)
#   species-image-lists/filter?tag=138&lang=de&_sort=localname:ASC&_start=0&_limit=16
#   [{"id":370,"speciesid":"herb_47c78ded","synonym":null,"sciname":"Cirsium arvense","group":"herb","species":370,"localname":"Acker-Kratzdistel","formats":{"large":{"ext":".jpg","url":"/uploads/large_ff55038201a052c32e8accc6_2c3084e6d6.jpg","hash":"large_ff55038201a052c32e8accc6_2c3084e6d6","mime":"image/jpeg","name":"large_ff55038201a052c32e8accc6.jpg","path":null,"size":113.26,"width":842,"height":1200},"small":{"ext":".jpg","url":"/uploads/small_ff55038201a052c32e8accc6_2c3084e6d6.jpg","hash":"small_ff55038201a052c32e8accc6_2c3084e6d6","mime":"image/jpeg","name":"small_ff55038201a052c32e8accc6.jpg","path":null,"size":20.96,"width":281,"height":400},"medium":{"ext":".jpg","url":"/uploads/medium_ff55038201a052c32e8accc6_2c3084e6d6.jpg","hash":"medium_ff55038201a052c32e8accc6_2c3084e6d6","mime":"image/jpeg","name":"medium_ff55038201a052c32e8accc6.jpg","path":null,"size":61.66,"width":561,"height":800},"thumbnail":{"ext":".jpg","url":"/uploads/thumbnail_ff55038201a052c32e8accc6_2c3084e6d6.jpg","hash":"thumbnail_ff55038201a052c32e8accc6_2c3084e6d6","mime":"image/jpeg","name":"thumbnail_ff55038201a052c32e8accc6.jpg","path":null,"size":5.02,"width":109,"height":156}}}, ...

# 4.)
# species/portrait?id=1569&lang=de
# json: siehe https://naturblick.museumfuernaturkunde.berlin/strapi/species/portrait?id=1569&lang=de

class SpeciesList(generics.ListAPIView):
    # queryset = Species.objects.all()

    def get_queryset(self):
        queryset = Species.objects.all()
        lang_filter = self.request.query_params.get('language')

        if lang_filter:
            queryset = queryset.filter(language=lang_filter)

        return queryset

    serializer_class = SpeciesSerializer

# class SpeciesDetail(APIView):
#     def get(self, request, species_id):
#         species = get_object_or_404(Species, id=species_id)
#         serializer = SpeciesSerializer(species)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# class CharacterValues(generics.ListAPIView):
#     queryset = CharacterValue.objects.order_by('id').all()
#     serializer_class = CharacterValueSerializer
