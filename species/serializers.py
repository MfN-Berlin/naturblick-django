from image_cropping.utils import get_backend
from rest_framework import serializers

from .models import Species, SpeciesName, Avatar, Tag, SimilarSpecies, GoodToKnow, UnambigousFeature, Source, \
    Faunaportrait, Floraportrait


class TagLocalnameField(serializers.Field):
    def to_representation(self, obj):
        request = self.context.get('request', None)
        lang = request.query_params.get('lang') if request else None

        if lang == 'en':
            return obj.english_name
        return obj.name


class TagSerializer(serializers.ModelSerializer):
    localname = TagLocalnameField(source='*')
    tag_id = serializers.IntegerField(source='id')

    class Meta:
        model = Tag
        fields = ['tag_id', 'localname']


class AvatarSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField('generate_avatar_url')

    def generate_avatar_url(self, avatar):
        return get_backend().get_thumbnail_url(
            avatar.image,
            {
                'size': (400, 400),
                'box': avatar.cropping,
                'crop': True,
                'detail': True,
            }
        )

    class Meta:
        model = Avatar
        fields = ['avatar_url', 'image_owner', 'image_ownerLink', 'image_source', 'image_license']


class SpeciesNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeciesName
        fields = ['name', 'language']


class SpeciesLocalnameField(serializers.Field):
    def to_representation(self, obj):
        request = self.context.get('request', None)
        lang = request.query_params.get('lang') if request else None

        if lang == 'en':
            return obj.engname
        return obj.gername


class SynonymField(serializers.Field):
    def to_representation(self, obj):
        speciesnames = [sn.name for sn in obj.prefetched_speciesnames]
        if speciesnames:
            return ", ".join(speciesnames)
        return ""


class SpeciesSerializer(serializers.ModelSerializer):
    localname = SpeciesLocalnameField(source='*')
    group = serializers.CharField(source='group.name', read_only=True)
    synonym = SynonymField(source='*')
    avatar_url = serializers.CharField(source="avatar.image.url", read_only=True)
    avatar_owner = serializers.CharField(source="avatar.owner", read_only=True)
    avatar_license = serializers.CharField(source="avatar.license", read_only=True)
    avatar_source = serializers.CharField(source="avatar.source", read_only=True)

    class Meta:
        model = Species
        fields = ['id', 'speciesid', 'localname', 'group', 'sciname', 'synonym', 'avatar_url', 'avatar_owner',
                  'avatar_license', 'avatar_source']


class UrlField(serializers.Field):
    def to_representation(self, obj):
        pif = obj.prefetched_portraits[0].descmeta.portrait_image_file
        return pif.small.url

class WidthField(serializers.Field):
    def to_representation(self, obj):
        pif = obj.prefetched_portraits[0].descmeta.portrait_image_file
        return pif.small.width

class HeightField(serializers.Field):
    def to_representation(self, obj):
        pif = obj.prefetched_portraits[0].descmeta.portrait_image_file
        return pif.small.height

class SimilarSpeciesLocalnameField(serializers.Field):
    def to_representation(self, obj):
        request = self.context.get('request', None)
        lang = (request.query_params.get('lang') if request else None)

        if lang == 'en':
            return obj.species.engname
        return obj.species.gername


class SimilarSpeciesSerilizer(serializers.ModelSerializer):
    sciname = serializers.CharField(source="species.sciname", read_only=True)
    similar_species_id = serializers.CharField(source="species.id", read_only=True)
    localname = SimilarSpeciesLocalnameField(source='*')

    class Meta:
        model = SimilarSpecies
        fields = ['differences', 'localname', 'sciname', 'similar_species_id']


class GoodtoknowSerilizer(serializers.ModelSerializer):
    class Meta:
        model = GoodToKnow
        fields = ['fact']


class UnambigousFeatureSerilizer(serializers.ModelSerializer):
    class Meta:
        model = UnambigousFeature
        fields = ['description']


class SourceSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ['text']


class PortraitSerializer(serializers.ModelSerializer):
    similar_species = SimilarSpeciesSerilizer(many=True, read_only=True, source='similarspecies_set')
    goodtoknow = GoodtoknowSerilizer(many=True, read_only=True, source='goodtoknow_set')
    unambigousfeature = UnambigousFeatureSerilizer(many=True, read_only=True, source='unambigousfeature_set')
    source = SourceSerilizer(many=True, read_only=True, source='source_set')

    description_image_orientation = serializers.CharField(source="descmeta.image_orientation", read_only=True)
    description_image_display_ratio = serializers.CharField(source="descmeta.display_ratio", read_only=True)
    description_image_grid_ratio = serializers.CharField(source="descmeta.grid_ratio", read_only=True)
    description_image_focus_point_vertical = serializers.FloatField(source="descmeta.focus_point_vertical",
                                                                    read_only=True)
    description_image_focus_point_horizontal = serializers.FloatField(source="descmeta.focus_point_horizontal",
                                                                      read_only=True)
    description_image_text = serializers.CharField(source="descmeta.text", read_only=True)
    description_image_small = serializers.URLField(source="descmeta.portrait_image_file.small.url", read_only=True)
    description_image_medium = serializers.URLField(source="descmeta.portrait_image_file.medium.url", read_only=True)
    description_image_large = serializers.URLField(source="descmeta.portrait_image_file.large.url", read_only=True)

    funfact_image_orientation = serializers.CharField(source="funfactmeta.image_orientation", read_only=True)
    funfact_image_display_ratio = serializers.CharField(source="funfactmeta.display_ratio", read_only=True)
    funfact_image_grid_ratio = serializers.CharField(source="funfactmeta.grid_ratio", read_only=True)
    funfact_image_focus_point_vertical = serializers.FloatField(source="funfactmeta.focus_point_vertical",
                                                                read_only=True)
    funfact_image_focus_point_horizontal = serializers.FloatField(source="funfactmeta.focus_point_horizontal",
                                                                  read_only=True)
    funfact_image_text = serializers.CharField(source="funfactmeta.text", read_only=True)
    funfact_image_small = serializers.URLField(source="funfactmeta.portrait_image_file.small.url",
                                                   read_only=True)
    funfact_image_medium = serializers.URLField(source="funfactmeta.portrait_image_file.medium.url",
                                                    read_only=True)
    funfact_image_large = serializers.URLField(source="funfactmeta.portrait_image_file.large.url",
                                                   read_only=True)

    inthecity_image_orientation = serializers.CharField(source="inthecitymeta.image_orientation", read_only=True)
    inthecity_image_display_ratio = serializers.CharField(source="inthecitymeta.display_ratio", read_only=True)
    inthecity_image_grid_ratio = serializers.CharField(source="inthecitymeta.grid_ratio", read_only=True)
    inthecity_image_focus_point_vertical = serializers.FloatField(source="inthecitymeta.focus_point_vertical",
                                                                  read_only=True)
    inthecity_image_focus_point_horizontal = serializers.FloatField(source="inthecitymeta.focus_point_horizontal",
                                                                    read_only=True)
    inthecity_image_text = serializers.CharField(source="inthecitymeta.text", read_only=True)
    inthecity_image_small = serializers.URLField(source="inthecitymeta.portrait_image_file.small.url",
                                               read_only=True)
    inthecity_image_medium = serializers.URLField(source="inthecitymeta.portrait_image_file.medium.url",
                                                read_only=True)
    inthecity_image_large = serializers.URLField(source="inthecitymeta.portrait_image_file.large.url",
                                               read_only=True)

    class Meta:
        fields = ['short_description', 'city_habitat', 'human_interaction', 'similar_species', 'goodtoknow',
                  'unambigousfeature', 'source',
                  'description_image_display_ratio',
                  'description_image_grid_ratio',
                  'description_image_focus_point_vertical',
                  'description_image_focus_point_horizontal',
                  'description_image_text',
                  'description_image_small',
                  'description_image_medium',
                  'description_image_large',
                  'funfact_image_display_ratio',
                  'funfact_image_grid_ratio',
                  'funfact_image_focus_point_vertical',
                  'funfact_image_focus_point_horizontal',
                  'funfact_image_text',
                  'funfact_image_small',
                  'funfact_image_medium',
                  'funfact_image_large',
                  'inthecity_image_display_ratio',
                  'inthecity_image_grid_ratio',
                  'inthecity_image_focus_point_vertical',
                  'inthecity_image_focus_point_horizontal',
                  'inthecity_image_text',
                  'inthecity_image_small',
                  'inthecity_image_medium',
                  'inthecity_image_large',
                  'similar_species',
                  'goodtoknow',
                  'unambigousfeature',
                  'source']


class FaunaPortraitSerializer(PortraitSerializer):
    audio_license = serializers.CharField(source="faunaportrait_audio_file.license", read_only=True)
    audio_url = serializers.CharField(source="faunaportrait_audio_file.audio_file.url", read_only=True)
    audio_specgram = serializers.CharField(source="faunaportrait_audio_file.audio_spectrogram.url", read_only=True)

    class Meta:
        model = Faunaportrait
        fields = PortraitSerializer.Meta.fields + ['male_description', 'female_description', 'juvenile_description',
                                                   'audio_title', 'audio_license', 'audio_url', 'audio_specgram']


class FloraportraitSerializer(PortraitSerializer):
    class Meta:
        model = Floraportrait
        fields = PortraitSerializer.Meta.fields + ['leaf_description', 'stem_axis_description', 'flower_description',
                                                   'fruit_description']

class SpeciesImageListSerializer(serializers.ModelSerializer):
    localname = SpeciesLocalnameField(source='*')
    group = serializers.CharField(source='group.name', read_only=True)
    synonym = SynonymField(source='*')

    avatar_url = serializers.CharField(source="avatar.image.url", read_only=True)

    desc_url = UrlField(source="*", required=True)
    desc_width = WidthField(source="*", required=True)
    desc_height = HeightField(source="*", required=True)

    class Meta:
        model = Species
        fields = ['id', 'localname', 'group', 'sciname', 'synonym', 'avatar_url', 'desc_url', 'desc_width', 'desc_height']
