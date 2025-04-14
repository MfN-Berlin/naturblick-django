import json
from pathlib import Path

from django.core import management
from django.db.models import Prefetch
from django.db.models import Q
from django.http import FileResponse, JsonResponse
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, server_error
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Species, Tag, SpeciesName, Floraportrait, Faunaportrait, GoodToKnow, Source, SimilarSpecies, \
    UnambigousFeature
from .serializers import SpeciesSerializer, TagSerializer, FaunaPortraitSerializer, \
    FloraportraitSerializer, SpeciesImageListSerializer, DescMetaSerializer, \
    FunfactMetaSerializer, InthecityMetaSerializer
from .utils import create_sqlite_file


def get_lang_queryparam(request):
    return request.query_params.get('lang') or 'de'


# returns sqlite database used by android/ios
def app_content_db(request):
    # generates small, medium, large version of imagekit Spec-Fields
    management.call_command("generateimages")

    sqlite_db = create_sqlite_file()

    response = FileResponse(open(sqlite_db, "rb"), as_attachment=True)
    response["Content-Disposition"] = f'attachment; filename="species-db.sqlite3"'

    return response


class AppContentCharacterValue(APIView):
    def get(self, request):
        base_dir = Path(__file__).resolve().parent.parent
        character_values_file = base_dir / 'species' / 'data' / 'character-values.json'

        try:
            with open(character_values_file, 'r') as f:
                data = json.load(f)

            return Response(data) # Response(data, status=status.HTTP_200_OK)
        except:
            server_error(request)


def filter_species_by_query(species_qs, query, lang):
    if not query:
        return species_qs

    if lang and (lang == 'de' or lang == 'dels'):
        return species_qs.filter(
            Q(sciname__icontains=query) | Q(gername__icontains=query) | Q(speciesname__name__icontains=query))
    elif lang and lang == 'en':
        return species_qs.filter(
            Q(sciname__icontains=query) | Q(engname__icontains=query) | Q(speciesname__name__icontains=query))
    else:
        return species_qs.filter(
            Q(sciname__icontains=query) | Q(engname__icontains=query) | Q(gername__icontains=query) | Q(
                speciesname__name__icontains=query))


def filter_species_tags(species_qs, tags):
    if not tags:
        return species_qs
    return species_qs.filter(tag__in=tags)


# 2.) This is the 'old' Tag endpoint, callable with
#  - /tags/filter?lang=de&tagsearch=&_limit=-1
# now just use /species/tags/?lang=en&tagsearch=ant
# or /species/tags/ for 'de' as default without any query
class TagsList(generics.ListAPIView):

    def get_queryset(self):
        queryset = Tag.objects.all()
        query = self.request.query_params.get('tagsearch')
        lang = get_lang_queryparam(self.request)
        tags = self.request.query_params.getlist('tag')

        if query:
            if lang and lang == 'en':
                queryset = queryset.filter(Q(english_name__icontains=query))
            else:
                queryset = queryset.filter(Q(name__icontains=query))

        # only those tags, that are left by filtering the already selected species
        if tags:
            species_ids_with_tags = Species.objects.filter(tag__in=tags).values_list('id', flat=True)
            queryset = queryset.filter(Q(species__id__in=species_ids_with_tags) & ~Q(id__in=tags)).distinct()

        if lang == 'en':
            queryset = queryset.order_by('engname')
        else:
            queryset = queryset.order_by('name')

        return queryset

    serializer_class = TagSerializer
    pagination_class = None


# 2.2) tags?id=20&id=21 LANG!
# Just returns tags-list depending on optional queryparams tag=x&tag=...
class SimpleTagsList(generics.ListAPIView):

    def get_queryset(self):
        queryset = Tag.objects.all()
        tags = self.request.query_params.getlist('tag')
        lang = get_lang_queryparam(self.request)

        if tags:
            queryset = queryset.filter(id__in=tags)

        if lang == 'en':
            queryset = queryset.order_by('engname')
        else:
            queryset = queryset.order_by('name')

        return queryset

    serializer_class = TagSerializer
    pagination_class = None


# 4.)      species/portrait?id=1569&lang=de (id means species_id not portrait_id)
#       or species/portrait?speciesid=bird_0123abcd&lang=de (speciesid means old fashioned species_id)
#
# json: siehe https://naturblick.museumfuernaturkunde.berlin/strapi/species/portrait?id=1569&lang=de

class PortraitDetail(generics.GenericAPIView):
    def get(self, request):
        id = request.query_params.get('id')  # int-id
        speciesid = request.query_params.get('speciesid')  # old fashioned species_id
        lang = get_lang_queryparam(self.request)

        species_qs = Species.objects.all().select_related('group', 'avatar').prefetch_related(
            Prefetch("speciesname_set", queryset=SpeciesName.objects.filter(language=lang),
                     to_attr="prefetched_speciesnames"))
        if id:
            species_qs = species_qs.filter(id=id)
        elif speciesid:
            species_qs = species_qs.filter(speciesid=speciesid)
        species_qs = species_qs.first()

        if not species_qs:
            raise NotFound()

        is_fauna = species_qs.group.nature == 'fauna'
        portrait_qs = Faunaportrait.objects.select_related('faunaportrait_audio_file', 'descmeta', 'funfactmeta',
                                                           'inthecitymeta') if is_fauna else Floraportrait.objects.select_related(
            'descmeta', 'funfactmeta', 'inthecitymeta')

        if id:
            portrait_qs = portrait_qs.filter(species__id=id)
        elif speciesid:
            portrait_qs = portrait_qs.filter(species__speciesid=speciesid)

        portrait_qs = (
            portrait_qs.prefetch_related(Prefetch('goodtoknow_set', queryset=GoodToKnow.objects.order_by('order')),
                                         Prefetch('unambigousfeature_set',
                                                  queryset=UnambigousFeature.objects.order_by('order')),
                                         Prefetch('similarspecies_set',
                                                  queryset=SimilarSpecies.objects.order_by('order')),
                                         Prefetch('source_set', queryset=Source.objects.order_by('order')))
            .filter(Q(language=lang) & Q(published=True)))

        portrait_qs = portrait_qs.first()

        if not portrait_qs:
            raise NotFound()

        species_serializer = SpeciesSerializer(species_qs, context={'request': request})
        portrait_serializer = FaunaPortraitSerializer(portrait_qs, context={'request': request}) if is_fauna \
            else FloraportraitSerializer(portrait_qs, context={'request': request})

        descmeta_serializer = DescMetaSerializer(portrait_qs)
        funfact_data = FunfactMetaSerializer(portrait_qs).data
        inthecity_data = InthecityMetaSerializer(portrait_qs).data

        return Response({
            **species_serializer.data,
            **portrait_serializer.data,
            'desc': descmeta_serializer.data,
            'funfact': funfact_data if funfact_data['text'] else None,
            'inthecity': inthecity_data if inthecity_data['text'] else None,
        })


# ordering by synonym is no more possible unless it becomes (direct) part of the query
def order_suffix(sort, lang):
    match sort:
        case 'sciname':
            return 'sciname'
        case _:
            if lang == 'en':
                return 'engname'
            else:
                return 'gername'


def sort_species(species_qs, sort_and_order, lang):
    (sort, order) = sort_and_order.split(':')
    order_prefix = '' if order.lower() == 'asc' else '-'
    return species_qs.order_by(f'{order_prefix}{order_suffix(sort, lang)}')


class SpeciesList(generics.ListAPIView):
    def get_queryset(self):
        lang = get_lang_queryparam(self.request)
        query = self.request.query_params.get('query')
        tags = self.request.query_params.getlist('tag')
        sort_and_order = self.request.query_params.get('sort') or 'localname:ASC'

        species_qs = (Species.objects.select_related('avatar', 'group')
        .prefetch_related(
            Prefetch("speciesname_set", queryset=SpeciesName.objects.filter(language=lang).order_by('name'),
                     to_attr="prefetched_speciesnames"),
            Prefetch(
                "portrait_set", to_attr="prefetched_portraits"
            )
        ))

        species_qs = filter_species_by_query(species_qs, query, lang)
        species_qs = filter_species_tags(species_qs, tags)
        species_qs = species_qs.filter(
            Q(avatar__isnull=False) & Q(portrait__language=lang) & Q(portrait__published=True) & Q(
                portrait__descmeta__portrait_image_file__isnull=False))
        species_qs = sort_species(species_qs, sort_and_order, lang)

        return species_qs.distinct()

    serializer_class = SpeciesImageListSerializer
