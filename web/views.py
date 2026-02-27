from datetime import datetime

import requests
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext as _
from functools import partial

from species.models import Species, Portrait, Floraportrait, Faunaportrait


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
    return web_render(request, "index", context={
        "header_class": "home"
    })


def about(request):
    return web_render(request, "about")


sources_ident_translations = {
    "page": ["Seite", "Page"],
    "wiki": ["Wikipedia, Die freie Enzyklopädie", "Wikipedia, The Free Encyclopedia"],
    "revision": ["Bearbeitungsstand", "Date of last revision"],
    "accessed": ["Abgerufen", "Accessed"],
    "version": ["Fassung", "version"],
    "volume": ["Band", "volume"],
    "editors": ["Hrsg.", "eds."],
    "nodate": ["o.J.", "n.d."],
    "in": ["In", ""],
    "published": ["veröffentlicht", "published"],
    "edition": ["Auflage", "edition"],
    "part": ["Teil", "part"],
    "changedby": ["verändert von", "changed by"]
}


def translate_ident(lang_index, source):
    for key, value in sources_ident_translations.items():
        source = source.replace(f'{{{{{key}}}}}', value[lang_index])
    return source


def source_from_image(meta):
    return (f'{meta.text}, {meta.image_file.owner}, {meta.image_file.license}, {meta.image_file.source}')



def sims(language, similar_species):
    return {
        "name": similar_species.species.engname if language == "en" else similar_species.species.gername,
        "sciname": similar_species.species.sciname,
        "differences": similar_species.differences,
        "url": reverse("portrait", kwargs={"id": similar_species.species.id}),
        "img": similar_species.species.avatar_new.imagefile.image.url
    }


def portrait(request, id):
    language = extract_language(request, allowed_langs={"de", "en"})
    species = Species.objects.get(id=id)

    is_fauna = True if species.group.nature == 'fauna' else False
    objects = Faunaportrait.objects if is_fauna else Floraportrait.objects
    template = 'faunaportrait' if is_fauna else 'floraportrait'

    portrait = (
        objects
        .select_related(
            "descmeta",
            "inthecitymeta",
            "funfactmeta",
        )
        .prefetch_related(
            "goodtoknow_set",
            "source_set",
            "unambigousfeature_set",
            "similarspecies_set__species__avatar_new__imagefile",
        )
        .get(species_id=id, language=language)
    )

    descriptions = [portrait.short_description, portrait.male_description, portrait.female_description, portrait.juvenile_description] if is_fauna else [portrait.short_description, portrait.leaf_description, portrait.stem_axis_description, portrait.flower_description, portrait.fruit_description]

    sources = [source_from_image(portrait.descmeta)]
    if portrait.inthecitymeta:
        sources.append(source_from_image(portrait.inthecitymeta))
    if portrait.funfactmeta:
        sources.append(source_from_image(portrait.funfactmeta))
    sources += list(portrait.source_set.values_list("text", flat=True))
    translate_with_lang = partial(translate_ident, 1 if language == "en" else 0)
    sources = list(map(translate_with_lang, sources))

    goodtoknows = {gtk.type: gtk.fact for gtk in portrait.goodtoknow_set.all().order_by("ordering")}
    additional_names = ", ".join(species.speciesname_set.filter(language=language).values_list("name", flat=True))
    similar_species = [sims(language, s) for s in portrait.similarspecies_set.all()]
    unambigousfeature = list(portrait.unambigousfeature_set.all().values_list("description", flat=True))

    audio = {
        "audio_title": portrait.audio_title,
        "licence": portrait.faunaportrait_audio_file.license,
        "url": portrait.faunaportrait_audio_file.audio_file.url,
        "png": f"{portrait.faunaportrait_audio_file.audio_file.url.replace("audio_files", "spectrogram_images")}.png"
    } if is_fauna else None

    return web_render(request, template, context={
        "id": id,
        "header_class": "portrait",
        "portrait": portrait,
        "descriptions": [ x for x in descriptions if x is not None],
        "inthecity": [x for x in [portrait.city_habitat, portrait.human_interaction] if x is not None],
        "goodtoknows": goodtoknows,
        "sources": sources,
        "additional_name": additional_names,
        "similar_species": similar_species,
        "unambigousfeatures": unambigousfeature,
        "audio": audio,
        "species_name": species.engname if language == "en" else species.gername
    })


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


def web_render(request, template: str, context={}) -> HttpResponse:
    language = translation.get_language()
    context["language"] = language
    try:
        get_template(f"web/{template}.{language}.html")
        return render(request, f"web/{template}.{language}.html", context)
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


def extract_language(request: WSGIRequest, allowed_langs={"de", "en", "dels"}):
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
