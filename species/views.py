import csv
import json
import os
import subprocess
import tempfile
from pathlib import Path

from django import forms
from django.core import management
from django.core.exceptions import BadRequest
from django.db import connection
from django.db.models import Prefetch
from django.http import FileResponse, HttpResponse
from django.utils import translation
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from naturblick import settings
from web.views import is_valid_or_raise
from .leicht_db import create_leicht_db, leicht_portrait
from .models import Portrait, Group, Species, SpeciesName, FaunaportraitAudioFile, Faunaportrait, Floraportrait
from .serializers import GroupSerializer, DescMetaSerializer
from .utils import create_sqlite_file
from .utils import cropped_image


def is_data_valid():
    return not Portrait.objects.filter(species__accepted_species__isnull=False, published=True).exists()


# returns sqlite database used by android/ios
def app_content_db(request):
    if (not is_data_valid()):
        raise RuntimeError('There are published artportraits connected to a synonym')

    sqlite_db = create_sqlite_file()

    response = FileResponse(open(sqlite_db, "rb"), as_attachment=True)
    response["Content-Disposition"] = f'attachment; filename="species-db.sqlite3"'

    return response


# returns sqlite database used by naturblick leicht android/ios
def app_content_leicht_db(request):
    # generates small, medium, large version of imagekit Spec-Fields
    management.call_command("generateimages")

    if (not is_data_valid()):
        raise RuntimeError('There are published artportraits connected to a synonym')

    sqlite_db = create_leicht_db()

    return FileResponse(open(sqlite_db, "rb"), as_attachment=True, filename='species-db.sqlite3')


# return CSV image list for naturblick leicht
def get_backend():
    pass


def app_content_leicht_image_list(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="leicht-image-list.csv"'},
    )

    writer = csv.writer(response)
    for portrait in leicht_portrait():
        writer.writerow(
            ('avatar', cropped_image(portrait.avatar.imagefile.image, portrait.avatar.cropping), portrait.id))
        writer.writerow(
            ('image', portrait.avatar.imagefile.image.url, portrait.id))

    return response


class AppContentCharacterValue(APIView):
    def get(self, request):
        base_dir = Path(__file__).resolve().parent.parent
        character_values_file = base_dir / 'species' / 'data' / 'character-values.json'

        with open(character_values_file, 'r') as f:
            data = json.load(f)
        return Response(data)


class GroupsList(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


@api_view(['GET'])
def specgram(request, filename):
    specgram_path = os.path.join(os.path.join(settings.MEDIA_ROOT, 'spectrogram_images'), filename)
    mp3 = filename.rsplit('.', 1)[0]
    mp3_path = os.path.join(os.path.join(settings.MEDIA_ROOT, 'audio_files'), mp3)

    with tempfile.NamedTemporaryFile(suffix=".wav") as wav, tempfile.NamedTemporaryFile(suffix=".png") as sox_png:
        subprocess.run(["ffmpeg", "-y", "-i", mp3_path, wav.name], check=True)

        sox_cmd = [
            "sox", wav.name, "-n",
            "remix", "1",
            "rate", "22.05k",
            "spectrogram",
            "-m", "-r",
            "-x", "700",
            "-y", "129",
            "-o", sox_png.name
        ]
        subprocess.run(sox_cmd, check=True)

        magick_cmd = [
            "magick", sox_png.name,
            "-alpha", "copy",
            "-fill", "white",
            "-colorize", "100%",
            "-gravity", "north",
            "-chop", "x10",
            specgram_path,
        ]
        subprocess.run(magick_cmd, check=True)
        return FileResponse(open(specgram_path, "rb"))


def get_accepted_portrait_species_id(lang, s_id):
    query = """
             SELECT
            COALESCE(p2.species_id, p1.species_id),
            CASE WHEN p2.species_id IS NOT NULL THEN s.sciname ELSE NULL END
        FROM species AS s
        LEFT JOIN portrait p1 ON p1.species_id = s.id AND p1.language = %s
        LEFT JOIN portrait p2 ON p2.species_id = s.accepted_species_id AND p2.language = %s
        WHERE s.id = %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [lang, lang, s_id])
        result = cursor.fetchone()

    if result:
        species_id, sciname = result
        return species_id, sciname
    else:
        return None, None



#
# called by playback HttpService and platform
class VolunteerImages(generics.GenericAPIView):
    class PortraitForm(forms.Form):
        id = forms.IntegerField(required=False)

        def clean(self):
            cleaned_data = super().clean()
            if not cleaned_data.get("id"):
                raise forms.ValidationError(
                    "id must be specified."
                )

    def get(self, request):
        lang = translation.get_language()
        form = self.PortraitForm(self.request.query_params)
        is_valid_or_raise(form)
        s_id = form.cleaned_data["id"]

        if s_id:
            species_id, _ = get_accepted_portrait_species_id(s_id=s_id, lang=lang)

            if not species_id:
                raise NotFound()

            species_qs = Species.objects.filter(id=species_id).first()

            is_fauna = species_qs.group.nature == 'fauna'
            portrait_qs = Faunaportrait.objects.select_related(
                'descmeta') if is_fauna else Floraportrait.objects.select_related('descmeta')

            portrait_qs = portrait_qs.filter(species__id=species_id)
            portrait_qs = portrait_qs.filter(language=lang).first()

            if not portrait_qs:
                raise NotFound()

            descmeta_serializer = DescMetaSerializer(portrait_qs)
        else:
            raise BadRequest()

        return Response(descmeta_serializer.data)
