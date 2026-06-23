from rest_framework import serializers

from .models import Group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["name", "image", "svg"]


class DescMetaSerializer(serializers.Serializer):
    image_orig = serializers.URLField(source="descmeta.image_file.image.url", read_only=True)
    image_large = serializers.URLField(source="descmeta.image_file.image_large.url", read_only=True)
