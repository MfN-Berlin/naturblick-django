from django.db.models import Prefetch
from django.db.models import Q
from django.http import FileResponse
from rest_framework import generics
from rest_framework.response import Response

from .models import Species, Tag, SpeciesName, Floraportrait, Faunaportrait
from .serializers import SpeciesSerializer, TagSerializer
from .utils import create_sqlite_file


# returns sqlite database used by android/ios
def app_content(request):
    """Django view that generates and serves an SQLite file."""

    sqlite_db = create_sqlite_file()

    response = FileResponse(open(sqlite_db, "rb"), as_attachment=True)
    response["Content-Disposition"] = f'attachment; filename="species-db.sqlite3"'

    return response


# 1.) This is the 'old' StrapiSpeciesFilter endpoint, callable with
#  - /species/lang=de&query=&_limit=30
#  - /species/lang=de&query=amsel&_limit=30
#  - /species/lang=de&query=&_limit=30&tag=1&tag=42
# now one has to call atleast '/species/?limit=10&offset=10' to get a paginated result (do not omit the limit and offset parameter)
# lang, query and tag parameter(s) are still possible
class SpeciesList(generics.ListAPIView):
    serializer_class = SpeciesSerializer

    def get_queryset(self):

        query = self.request.query_params.get('query')
        lang = self.request.query_params.get('lang') or 'de'
        tag = self.request.query_params.getlist('tag')

        species_manager = Species.objects.select_related('avatar', 'group').prefetch_related(
            Prefetch("speciesname_set", queryset=SpeciesName.objects.filter(language=lang),
                     to_attr="prefetched_speciesnames")
        )

        if query:
            if lang and lang == 'de':
                queryset = species_manager.filter(
                    Q(sciname__icontains=query) | Q(gername__icontains=query) | Q(speciesname__name__icontains=query))
            elif lang and lang == 'en':
                queryset = species_manager.filter(
                    Q(sciname__icontains=query) | Q(engname__icontains=query) | Q(speciesname__name__icontains=query))
            else:
                queryset = species_manager.filter(
                    Q(sciname__icontains=query) | Q(engname__icontains=query) | Q(gername__icontains=query) | Q(
                        speciesname__name__icontains=query))
        else:
            queryset = species_manager.all()

        if tag:
            queryset = queryset.filter(tag__in=tag)

        return queryset.filter(Q(portrait__isnull=False) & Q(portrait__published=True) & Q(portrait__language=lang) & Q(
            avatar__isnull=False))


# 2.) This is the 'old' Tag endpoint, callable with
#  - /tags/filter?lang=de&tagsearch=&_limit=-1
# now just use /species/tags/?lang=en&tagsearch=ant
# or /species/tags/ for 'de' as default without any query
class TagsList(generics.ListAPIView):

    def get_queryset(self):
        queryset = Tag.objects.all()
        query = self.request.query_params.get('tagsearch')
        # defaults to 'de'
        lang = self.request.query_params.get('lang')

        if query:
            if lang and lang == 'en':
                queryset = queryset.filter(Q(english_name__icontains=query))
            else:
                queryset = queryset.filter(Q(name__icontains=query))

        return queryset

    serializer_class = TagSerializer
    pagination_class = None


# 3.)
#   species-image-lists/filter?tag=138&lang=de&_sort=localname:ASC&_start=0&_limit=16
#   [{"id":370,"speciesid":"herb_47c78ded","synonym":null,"sciname":"Cirsium arvense","group":"herb","species":370,"localname":"Acker-Kratzdistel","formats":{"large":{"ext":".jpg","url":"/uploads/large_ff55038201a052c32e8accc6_2c3084e6d6.jpg","hash":"large_ff55038201a052c32e8accc6_2c3084e6d6","mime":"image/jpeg","name":"large_ff55038201a052c32e8accc6.jpg","path":null,"size":113.26,"width":842,"height":1200},"small":{"ext":".jpg","url":"/uploads/small_ff55038201a052c32e8accc6_2c3084e6d6.jpg","hash":"small_ff55038201a052c32e8accc6_2c3084e6d6","mime":"image/jpeg","name":"small_ff55038201a052c32e8accc6.jpg","path":null,"size":20.96,"width":281,"height":400},"medium":{"ext":".jpg","url":"/uploads/medium_ff55038201a052c32e8accc6_2c3084e6d6.jpg","hash":"medium_ff55038201a052c32e8accc6_2c3084e6d6","mime":"image/jpeg","name":"medium_ff55038201a052c32e8accc6.jpg","path":null,"size":61.66,"width":561,"height":800},"thumbnail":{"ext":".jpg","url":"/uploads/thumbnail_ff55038201a052c32e8accc6_2c3084e6d6.jpg","hash":"thumbnail_ff55038201a052c32e8accc6_2c3084e6d6","mime":"image/jpeg","name":"thumbnail_ff55038201a052c32e8accc6.jpg","path":null,"size":5.02,"width":109,"height":156}}}, ...

# 4.) old: species/portrait?id=1569&lang=de (id means species_id not portrait_id)
#
# json: siehe https://naturblick.museumfuernaturkunde.berlin/strapi/species/portrait?id=1569&lang=de

class PortraitDetail(generics.GenericAPIView):
    def get(self, request):
        species_id = request.query_params.get('id')  # int-id
        lang = request.query_params.get('lang') or 'de'

        species = Species.objects.all().select_related('group', 'avatar').prefetch_related(
            Prefetch("speciesname_set", queryset=SpeciesName.objects.filter(language=lang))).filter(
            id=species_id).first()
        manager = Faunaportrait.objects if species.group.nature == 'fauna' else Floraportrait.objects
        portrait = manager.prefetch_related('goodtoknow_set', 'unambigousfeature_set', 'similarspecies_set',
                                            'source_set').filter(Q(species__id=species_id) & Q(language=lang)).first()

        #    data_a = ModelA.objects.all()  # You can apply filters or other logic here
        #    data_b = ModelB.objects.all()

        # Serialize data for both models
        #   serializer_a = ModelASerializer(data_a)
        #   serializer_b = ModelBSerializer(data_b, many=True) #  if many =)

        # Concatenate the two serialized data into a single dictionary
        combined_data = {}  # {**serializer_a.data, **serializer_b.data}

        # Return the combined data as JSON response
        return Response(combined_data)

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
