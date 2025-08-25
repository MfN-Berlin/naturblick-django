import os

from image_cropping.utils import get_backend
from rest_framework import serializers

from .models import Species, SpeciesName, Tag, SimilarSpecies, GoodToKnow, UnambigousFeature, Source, \
    Faunaportrait, Floraportrait, PlantnetPowoidMapping, Group


def avatar_crop_url(avatar):
    return get_backend().get_thumbnail_url(
        avatar.image,
        {
            'size': (400, 400),
            'box': avatar.cropping,
            'crop': True,
            'detail': True,
        }
    )


class AvatarCropUrlField(serializers.Field):
    def to_representation(self, obj):
        if not obj:
            return None
        return avatar_crop_url(obj)


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
        speciesnames = [sn.name for sn in obj]
        if speciesnames:
            return ", ".join(speciesnames)
        return None


class Mp3Url(serializers.Field):
    def to_representation(self, obj):
        if len(obj) > 0 and obj[0]:
            return obj[0].audio_file.url
        return None


class SpeciesSerializer(serializers.ModelSerializer):
    localname = SpeciesLocalnameField(source='*', read_only=True)
    group = serializers.CharField(source='group.name', read_only=True)
    synonym = SynonymField(source='prefetched_speciesnames')
    avatar_url = AvatarCropUrlField(source="avatar")
    avatar_owner = serializers.CharField(source="avatar.owner", read_only=True)
    avatar_license = serializers.CharField(source="avatar.license", read_only=True)
    avatar_source = serializers.CharField(source="avatar.source", read_only=True)
    audio_filename = serializers.SerializerMethodField(method_name="create_audio_filename")

    class Meta:
        model = Species
        fields = ['id', 'speciesid', 'localname', 'group', 'sciname', 'synonym', 'avatar_url', 'avatar_owner',
                  'avatar_license', 'avatar_source', 'red_list_germany', 'audio_filename']

    def create_audio_filename(self, obj):
        if obj.prefetched_audiofile:
            return os.path.basename(obj.prefetched_audiofile[0].audio_file.name)
        else:
            return None


class UrlField(serializers.Field):
    def to_representation(self, obj):
        pif = obj[0].descmeta.portrait_image_file
        return pif.image_small.url


class WidthField(serializers.Field):
    def to_representation(self, obj):
        pif = obj[0].descmeta.portrait_image_file
        return pif.image_small.width


class HeightField(serializers.Field):
    def to_representation(self, obj):
        pif = obj[0].descmeta.portrait_image_file
        return pif.image_small.height


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
    avatar_url = AvatarCropUrlField(
        source='species.avatar')  # serializers.URLField(source="species.avatar.image.url", read_only=True)
    localname = SimilarSpeciesLocalnameField(source='*')
    speciesid = serializers.CharField(source="species.speciesid", read_only=True)
    group = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = SimilarSpecies
        fields = ['differences', 'localname', 'sciname', 'similar_species_id', 'avatar_url', 'has_portrait',
                  'speciesid', 'group']


class GoodtoknowSerilizer(serializers.ModelSerializer):
    text = serializers.CharField(source="fact")
    type = serializers.CharField()

    class Meta:
        model = GoodToKnow
        fields = ['text', 'type']


class UnambigousFeatureSerilizer(serializers.ModelSerializer):
    text = serializers.CharField(source="description")

    class Meta:
        model = UnambigousFeature
        fields = ['text']


class SourceSerilizer(serializers.ModelSerializer):
    source = serializers.CharField(source="text", read_only=True)
    id = serializers.IntegerField(source="order", read_only=True)

    class Meta:
        model = Source
        fields = ['id', 'source']


class DescMetaSerializer(serializers.Serializer):
    image_orientation = serializers.CharField(source="descmeta.image_orientation", read_only=True)
    display_ratio = serializers.CharField(source="descmeta.display_ratio", read_only=True)
    grid_ratio = serializers.CharField(source="descmeta.grid_ratio", read_only=True)
    focus_point_vertical = serializers.FloatField(source="descmeta.focus_point_vertical", read_only=True)
    focus_point_horizontal = serializers.FloatField(source="descmeta.focus_point_horizontal", read_only=True)
    text = serializers.CharField(source="descmeta.text", read_only=True)
    image_orig = serializers.URLField(source="descmeta.portrait_image_file.image.url", read_only=True)
    image_orig_width = serializers.IntegerField(source="descmeta.portrait_image_file.width", read_only=True)
    image_orig_height = serializers.IntegerField(source="descmeta.portrait_image_file.height", read_only=True)
    image_small = serializers.URLField(source="descmeta.portrait_image_file.image_small.url", read_only=True)
    image_medium = serializers.URLField(source="descmeta.portrait_image_file.image_medium.url", read_only=True)
    image_large = serializers.URLField(source="descmeta.portrait_image_file.image_large.url", read_only=True)
    image_large_width = serializers.IntegerField(source="descmeta.portrait_image_file.image_large.width",
                                                 read_only=True)
    image_large_height = serializers.IntegerField(source="descmeta.portrait_image_file.image_large.height",
                                                  read_only=True)
    owner = serializers.CharField(source="descmeta.portrait_image_file.owner", read_only=True)
    owner_link = serializers.CharField(source="descmeta.portrait_image_file.owner_link", read_only=True)
    source = serializers.CharField(source="descmeta.portrait_image_file.source", read_only=True)
    license = serializers.CharField(source="descmeta.portrait_image_file.license", read_only=True)


class FunfactMetaSerializer(serializers.Serializer):
    image_orientation = serializers.CharField(source="funfactmeta.image_orientation", read_only=True)
    display_ratio = serializers.CharField(source="funfactmeta.display_ratio", read_only=True)
    grid_ratio = serializers.CharField(source="funfactmeta.grid_ratio", read_only=True)
    focus_point_vertical = serializers.FloatField(source="funfactmeta.focus_point_vertical", read_only=True)
    focus_point_horizontal = serializers.FloatField(source="funfactmeta.focus_point_horizontal", read_only=True)
    text = serializers.CharField(source="funfactmeta.text", read_only=True)
    image_orig = serializers.URLField(source="funfactmeta.portrait_image_file.image.url", read_only=True)
    image_orig_width = serializers.IntegerField(source="funfactmeta.portrait_image_file.width", read_only=True)
    image_small = serializers.URLField(source="funfactmeta.portrait_image_file.image_small.url", read_only=True)
    image_medium = serializers.URLField(source="funfactmeta.portrait_image_file.image_medium.url", read_only=True)
    image_large = serializers.URLField(source="funfactmeta.portrait_image_file.image_large.url", read_only=True)
    owner = serializers.CharField(source="funfactmeta.portrait_image_file.owner", read_only=True)
    owner_link = serializers.CharField(source="funfactmeta.portrait_image_file.owner_link", read_only=True)
    source = serializers.CharField(source="funfactmeta.portrait_image_file.source", read_only=True)
    license = serializers.CharField(source="funfactmeta.portrait_image_file.license", read_only=True)


class InthecityMetaSerializer(serializers.Serializer):
    image_orientation = serializers.CharField(source="inthecitymeta.image_orientation", read_only=True)
    display_ratio = serializers.CharField(source="inthecitymeta.display_ratio", read_only=True)
    grid_ratio = serializers.CharField(source="inthecitymeta.grid_ratio", read_only=True)
    focus_point_vertical = serializers.FloatField(source="inthecitymeta.focus_point_vertical", read_only=True)
    focus_point_horizontal = serializers.FloatField(source="inthecitymeta.focus_point_horizontal", read_only=True)
    text = serializers.CharField(source="inthecitymeta.text", read_only=True)
    image_orig = serializers.URLField(source="inthecitymeta.portrait_image_file.image.url", read_only=True)
    image_orig_width = serializers.IntegerField(source="inthecitymeta.portrait_image_file.width", read_only=True)
    image_small = serializers.URLField(source="inthecitymeta.portrait_image_file.image_small.url", read_only=True)
    image_medium = serializers.URLField(source="inthecitymeta.portrait_image_file.image_medium.url", read_only=True)
    image_large = serializers.URLField(source="inthecitymeta.portrait_image_file.image_large.url", read_only=True)
    owner = serializers.CharField(source="inthecitymeta.portrait_image_file.owner", read_only=True)
    owner_link = serializers.CharField(source="inthecitymeta.portrait_image_file.owner_link", read_only=True)
    source = serializers.CharField(source="inthecitymeta.portrait_image_file.source", read_only=True)
    license = serializers.CharField(source="inthecitymeta.portrait_image_file.license", read_only=True)


class PortraitSerializer(serializers.ModelSerializer):
    similar_species = SimilarSpeciesSerilizer(many=True, read_only=True, source='similarspecies_set')
    goodtoknow = GoodtoknowSerilizer(many=True, read_only=True, source='goodtoknow_set')
    unambigousfeature = UnambigousFeatureSerilizer(many=True, read_only=True, source='unambigousfeature_set')
    sources = SourceSerilizer(many=True, read_only=True, source='source_set')

    class Meta:
        fields = ['short_description',
                  'city_habitat',
                  'human_interaction',
                  'similar_species',
                  'goodtoknow',
                  'unambigousfeature',
                  'similar_species',
                  'goodtoknow',
                  'unambigousfeature',
                  'sources']


class FaunaPortraitSerializer(PortraitSerializer):
    audio_license = serializers.CharField(source="faunaportrait_audio_file.license", read_only=True)
    audio_filename = serializers.SerializerMethodField(method_name="create_audio_filename")
    is_floraportrait = serializers.BooleanField(default=False, read_only=True)

    class Meta:
        model = Faunaportrait
        fields = PortraitSerializer.Meta.fields + ['male_description', 'female_description', 'juvenile_description',
                                                   'audio_title', 'audio_license', 'audio_filename', 'is_floraportrait']

    def create_audio_filename(self, obj):
        try:
            return os.path.basename(obj.faunaportrait_audio_file.audio_file.name)
        except AttributeError:
            return None


class FloraportraitSerializer(PortraitSerializer):
    is_floraportrait = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = Floraportrait
        fields = PortraitSerializer.Meta.fields + ['leaf_description', 'stem_axis_description', 'flower_description',
                                                   'fruit_description', 'is_floraportrait']


class SpeciesImageListSerializer(serializers.ModelSerializer):
    localname = SpeciesLocalnameField(source='*')
    group = serializers.CharField(source='group.name', read_only=True)
    synonym = SynonymField(source='prefetched_speciesnames')

    avatar_url = AvatarCropUrlField(source="avatar")

    desc_url = UrlField(source="prefetched_portraits", required=True)
    desc_width = WidthField(source="prefetched_portraits", required=True)
    desc_height = HeightField(source="prefetched_portraits", required=True)

    class Meta:
        model = Species
        fields = ['id', 'localname', 'group', 'sciname', 'synonym', 'avatar_url', 'desc_url', 'desc_width',
                  'desc_height']


class PlantnetPowoidMappingSeralizer(serializers.ModelSerializer):
    class Meta:
        model = PlantnetPowoidMapping
        fields = ['plantnetpowoid', 'species_plantnetpowoid']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["name", "image", "svg"]
