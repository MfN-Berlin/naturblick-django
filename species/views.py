import csv
import json
import os
import subprocess
import tempfile
from pathlib import Path

from django.core import management
from django.http import FileResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from naturblick import settings
from .leicht_db import create_leicht_db, leicht_portrait
from .models import Portrait
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
        writer.writerow(('recognize', portrait.avatar.imagefile.image.url, portrait.id))
        writer.writerow(('goodtoknow', portrait.goodtoknow_image.image.url, portrait.id))

        if hasattr(portrait, 'audio') and portrait.audio:
            writer.writerow(('audio', portrait.audio.audio_file.url, portrait.id))

    return response


class AppContentCharacterValue(APIView):
    def get(self, request):
        base_dir = Path(__file__).resolve().parent.parent
        character_values_file = base_dir / 'species' / 'data' / 'character-values.json'

        with open(character_values_file, 'r') as f:
            data = json.load(f)
        return Response(data)


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
