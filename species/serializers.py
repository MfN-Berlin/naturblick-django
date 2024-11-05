from rest_framework import serializers
from .models import Species, SpeciesName


class SpeciesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Species
        fields = ['pk', 'sciname']


class SpeciesNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeciesName
        fields = ['name', 'language']

class SpeciesDetailSerializer(serializers.ModelSerializer):
    species_names = SpeciesNameSerializer(many=True, read_only=True)

    class Meta:
        model = Species
        fields = [
            'speciesid', 'sciname', 'group', 'wikipedia', 'name_de', 'name_en',
            'name_er', 'red_list_germany', 'iucncategory', 'activity_start_month',
            'activity_end_month', 'activity_start_hour', 'activity_end_hour',
            'accepted', 'species_names'
        ]
