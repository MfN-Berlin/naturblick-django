import requests
from django.conf import settings
from django.http import HttpResponse


def audio_proxy(request, obs_id):
    url = f"{settings.PLAYBACK_URL}projects/observations/{obs_id}/audio.mp4"
    r = requests.get(url, stream=True)

    return HttpResponse(
        r.iter_content(chunk_size=8192),
        content_type=r.headers.get("Content-Type", "video/mp4")
    )

def specgram_proxy(request, obs_id):
    url = f"{settings.PLAYBACK_URL}projects/observations/{obs_id}/audio.mp4.png"
    r = requests.get(url, stream=True)

    return HttpResponse(
        r.iter_content(chunk_size=8192),
        content_type=r.headers.get("Content-Type", "image/png")
    )

def image_proxy(request, obs_id):
    url = f"{settings.PLAYBACK_URL}projects/observations/{obs_id}/image.jpg"
    r = requests.get(url, stream=True)

    return HttpResponse(
        r.iter_content(chunk_size=8192),
        content_type=r.headers.get("Content-Type", "image/jpg")
    )

