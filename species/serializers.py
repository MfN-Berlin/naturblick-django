from image_cropping.utils import get_backend
from rest_framework import serializers

from .models import Species, SpeciesName, Avatar, Tag


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


# {"id":1,"speciesid":"amphibian_0de18656","localname":"Teichmolch","group":"amphibian","sciname":"Lissotriton vulgaris","synonym":null,"url":"/uploads/crop_d60f7f6c98b0fcf1aa52e7b0_f0b5f2e568.jpg","imageOwner":"Piet Spaans Viridiflavus","imageLicense":"CC BY-SA 2.5","imageSource":"https://commons.wikimedia.org/wiki/File:LissotritonVulgarisMaleWater.JPG"}
class SpeciesSerializer(serializers.ModelSerializer):
    localname = SpeciesLocalnameField(source='*')
    group = serializers.CharField(source='group.name', read_only=True)
    synonym = SynonymField(source='*')
    url = serializers.CharField(source="avatar.image.url", read_only=True)
    image_owner = serializers.CharField(source="avatar.owner", read_only=True)
    image_license = serializers.CharField(source="avatar.license", read_only=True)
    image_source = serializers.CharField(source="avatar.source", read_only=True)

    class Meta:
        model = Species
        fields = ['id', 'speciesid', 'localname', 'group', 'sciname', 'synonym', 'url', 'image_owner',
                  'image_license', 'image_source']


class CustomResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    data = serializers.ListField(child=serializers.DictField())
