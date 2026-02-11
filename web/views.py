from datetime import datetime
from typing import Any

import requests
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext as _

from species.models import Species, Portrait


class Og:
    def __init__(self, property, content):
        self.property = property
        self.content = content


def home(request):
    description = _("Discover Nature")
    ogs_list = [Og("og:title", "Naturblick"),
                Og("og:description", description),
                Og("og:twitter:image",
                   "https://naturblick.museumfuernaturkunde.berlin/strapi/uploads/large_Header_2023_klein_beschnitten_belichted_7cca538a55.jpg"),
                Og("og:twitter:image",
                   "https://naturblick.museumfuernaturkunde.berlin/strapi/uploads/large_Header_2023_klein_beschnitten_belichted_7cca538a55.jpg"),
                Og("og:image:width", 1200),
                Og("og:image:height", 521)
                ] + default_ogs(request)

    return render(request, "web/base.html", {"og_list": ogs_list})


def artportrait(request, id):
    lang = extract_language(request)

    p = Portrait.objects.filter(species_id=id, language=lang).first()
    ogs_list = []
    if p:
        ogs_list.append(Og("og:description", p.short_description))
        ogs_list.append(Og("og:title", p.species.engname if lang == "en" else p.species.gername))

        desc_meta = p.descmeta
        if desc_meta:
            image = desc_meta.image_file.large if desc_meta.image_file.large else desc_meta.image_file.image
            ogs_list = add_image_ogs(request, ogs_list, image)

    return default_response(request, ogs_list)


def old_artportrait(request, species_id):
    lang = extract_language(request)
    int_id = Species.objects.filter(speciesid=species_id).values_list(
        "id", flat=True).first()

    if int_id:
        url = reverse("artportrait", kwargs={"id": int_id})
        return redirect(f"{url}?lang={lang}", permanent=True)
    else:
        return default_response(request, [])


# for subsites like Wissensweiten
def sub_page(request):
    return default_response(request, [])


def map_page(request, obs_id):
    lang = extract_language(request)
    ogs_list = []

    try:
        json = requests.get(f"https://naturblick.museumfuernaturkunde.berlin/api/projects/observations/{obs_id}").json()
        species_id = json["data"]["species"]
        s = Species.objects.filter(id=species_id).first()
        cc_name = json["data"]["ccName"]
        date_time = datetime.fromisoformat(json["data"]["dateTime"])
        date = date_time.strftime("%d.%m.%Y")
        coords = json["data"]["coords"]["coordinates"]

        ogs_list.append(Og("og:title", s.engname if lang == "en" else s.gername))

        obs_type = json["data"]["obsType"]
        if obs_type in ["image", "unidentifiedimage"]:
            ogs_list.append(Og("og:image",
                               f"https://naturblick.museumfuernaturkunde.berlin/api/projects/observations/{obs_id}/image.jpg"))
            ogs_list.append(Og("og:twitter:image",
                               f"https://naturblick.museumfuernaturkunde.berlin/api/projects/observations/{obs_id}/image.jpg"))
        elif obs_type in ["audio", "unidentifiedaudio"]:
            ogs_list.append(Og("og:audio",
                               f"https://naturblick.museumfuernaturkunde.berlin/api/projects/observations/{obs_id}/audio.mp4"))

        ogs_list.append(Og("og:description",
                           seen_by(cc_name, date, coords)))
    except:
        pass

    return default_response(request, ogs_list)


def index(request):
    return web_render(request, "index", context = {
        "header_class": "home"
    })

def about(request):
    return web_render(request, "about")


def mobileapp(request):
    return web_render(request, "mobileapp")


def faq(request):
    return web_render(request, "faq")


def kontakt(request):
    return web_render(request, "contact")


def privacy(request):
    return web_render(request, "privacy")


def imprint(request):
    return web_render(request, "imprint")


def web_render(request, template: str, context=None) -> HttpResponse:
    lang = translation.get_language()
    try:
        get_template(f"web/{template}.{lang}.html")
        return render(request, f"web/{template}.{lang}.html", context)
    except TemplateDoesNotExist:
        print("Fallback to DE ")
        return render(request, f"web/{template}.de.html", context)


def digitalaccessibilitystatement(request):
    return web_render(request, "digitalaccessibilitystatement")


def default_response(request, more_ogs=None):
    if more_ogs is None:
        more_ogs = []
    ogs_list = more_ogs + default_ogs(request)

    return render(request, "web/base.html", {"og_list": ogs_list})


def default_ogs(request: WSGIRequest) -> list[Og]:
    return [Og("og:type", "website"),
            Og("og:site-name", "Naturblick"),
            Og("og:url", og_url(request))
            ]


def extract_language(request: WSGIRequest | Any):
    allowed_langs = {"de", "en", "dels"}
    lang = request.GET.get("lang", "de")
    if lang not in allowed_langs:
        lang = "de"
    return lang


def og_url(request):
    return f'{request.get_host()}{request.get_full_path().replace("/index", "")}'


def seen_by(user, date, coords):
    return _("Seen by {user} at {date} in {coords}").format(user=user, date=date, coords=coords)


def add_image_ogs(request, ogs_list, image):
    ogs_list.append(Og("og:image:width", image.width))
    ogs_list.append(Og("og:image:height", image.height))
    ogs_list.append(Og("og:image", f'{request.get_host()}{image.url}'))
    ogs_list.append(Og("og:twitter:image", f'{request.get_host()}{image.url}'))
    return ogs_list
