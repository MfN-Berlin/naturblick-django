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


class SpeciesNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeciesName
        fields = ['name', 'language', 'isPrimary']


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


class SpeciesDetailSerializer(serializers.ModelSerializer):
    species_names = SpeciesNameSerializer(many=True, read_only=True)
    avatar = AvatarSerializer(read_only=True)
    female_avatar = AvatarSerializer(read_only=True)

    class Meta:
        model = Species
        fields = [
            'speciesid', 'group', 'wikipedia', 'red_list_germany', 'iucncategory', 'activity_start_month',
            'activity_end_month', 'activity_start_hour', 'activity_end_hour',
            'accepted', 'species_names', 'avatar', 'female_avatar'
        ]
