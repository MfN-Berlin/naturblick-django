from image_cropping.utils import get_backend
from rest_framework import serializers

from .models import Species, SpeciesName, Avatar, CharacterValue


class CharacterValueSerializer(serializers.ModelSerializer):
    character_id = serializers.IntegerField(source='character.id')

    class Meta:
        model = CharacterValue
        fields = ['id',
                  'character_id',
                  'gername',
                  'engname',
                  'colors',
                  'dots',
                  'image']


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ['pk', 'speciesid']


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


# /species/{id}
# expects `Species`    species/1
# export interface SpeciesName { name: string, language: number }
#
# export interface Species {
#   id: number;
#   speciesid: string,
#   group: string,
#   sciname: string,
#   gername: string,
#   engname: string,
#   speciesnames: SpeciesName[] }

class SpeciesNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeciesName
        fields = ['name', 'language']


class SpeciesSerializer(serializers.ModelSerializer):
    species_names = SpeciesNameSerializer(source='speciesname_set', many=True, read_only=True)

    class Meta:
        model = Species
        fields = ['id', 'speciesid', 'group', 'sciname', 'gername', 'engname', 'species_names']
