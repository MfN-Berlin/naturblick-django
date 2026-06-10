import json
import os
from datetime import datetime, timezone
from functools import partial
from urllib.parse import quote

import markdown
import requests
from django import forms
from django.conf import settings
from django.core.exceptions import BadRequest
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Prefetch, Q
from django.http import \
    Http404, \
    HttpResponse, \
    JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse
from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from rest_framework.exceptions import NotFound

from species.models import Species, Portrait, Floraportrait, Faunaportrait, Tag, EvaluationAuthor
from web.utils import from_time, response_json


class Og:
    def __init__(self, property, content):
        self.property = property
        self.content = content


def old_artportrait(request, species_id):
    lang = translation.get_language()
    int_id = Species.objects.filter(speciesid=species_id).values_list(
        "id", flat=True).first()

    if not int_id:
        raise NotFound("Species not found")
    url = reverse("portrait", kwargs={"id": int_id})
    return redirect(f"{url}?lang={lang}", permanent=True)


def index(request):
    lang = translation.get_language()
    species_qs = (Species.objects.select_related('avatar_new', 'group').prefetch_related(
        Prefetch(
            "portrait_set", to_attr="prefetched_portraits"
        )
    ))
    ids = [370, 12, 160, 701, 73, 639, 661, 713]
    if lang == "dels":
        ids = [370, 73, 160, 701, 704, 639, 661, 713]

    species_qs = species_qs.filter(id__in=ids)
    species_dict = {
        s.id: (
            s.id,
            s.prefetched_portraits[0].descmeta.image_file.image_small.url,
            s.prefetched_portraits[0].descmeta.image_file.image_small.width,
            s.prefetched_portraits[0].descmeta.image_file.image_small.height,
            s.group,
            s.name(lang),
            s.sciname
        ) for s in species_qs

    }
    species = [species_dict[id] for id in ids]
    description = _("Entdecke die Natur")
    ogs_list = [Og("og:title", "Naturblick"),
                Og("og:description", description),
                Og("og:twitter:image",
                   "https://naturblick.museumfuernaturkunde.berlin/strapi/uploads/large_Header_2023_klein_beschnitten_belichted_7cca538a55.jpg"),
                Og("og:twitter:image",
                   "https://naturblick.museumfuernaturkunde.berlin/strapi/uploads/large_Header_2023_klein_beschnitten_belichted_7cca538a55.jpg"),
                Og("og:image:width", 1200),
                Og("og:image:height", 521)
                ] + default_ogs(request)
    return web_render(request, "index", context={
        "lang": lang,
        "dark": True,
        "species": species,
        "og_list": ogs_list
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
    return f'{meta.text}, {meta.image_file.owner}, {meta.image_file.license}, {meta.image_file.source}'


def sims(language, similar_species):
    return {
        "name": similar_species.species.engname if language == "en" else similar_species.species.gername,
        "sciname": similar_species.species.sciname,
        "differences": similar_species.differences,
        "url": reverse("portrait", kwargs={"id": similar_species.species.id}) if Portrait.objects.filter(
            species=similar_species.species.id).exists() else None,
        "img": similar_species.species.avatar_new.imagefile.image.url if similar_species.species.avatar_new else None
    }


def endangerstatus(species, language):
    if not species.red_list_germany:
        return None

    if language == "en":
        endangervalue = "Endangerment level Germany: <mark class=\""
        match species.red_list_germany:
            case 'gefahrdet':
                endangervalue += 'orange\">endangered</mark>'
            case 'Vorwarnliste':
                endangervalue += 'orange\">Warning list</mark>'
            case 'ausgestorbenOderVerschollen':
                endangervalue += 'red\">extinct or missing</mark>'
            case 'vomAussterbenBedroht':
                endangervalue += 'red\">threatened with extinction</mark>'
            case 'starkGefahrdet':
                endangervalue += 'red\">severely endangered</mark>'
            case 'GefahrdungUnbekanntenAusmasses':
                endangervalue += 'gray\">endangerment unknown</mark>'
            case 'extremSelten':
                endangervalue += 'orange\">extremly rare</mark>'
            case 'DatenUnzureichend':
                endangervalue += 'gray\">insufficient data available</mark>'
            case 'ungefahrdet':
                endangervalue += 'green\">not endangered</mark>'
            case 'nichtBewertet':
                endangervalue += 'gray\">not evaluated</mark>'
            case 'keinNachweis':
                endangervalue += 'gray\">no proof</mark>'
            case _:
                return None
        return mark_safe(endangervalue)
    else:
        endangervalue = "Gefährdungsstatus Deutschland: <mark class=\""
        match species.red_list_germany:
            case 'gefahrdet':
                endangervalue += 'orange\">gefährdet</mark>'
            case 'Vorwarnliste':
                endangervalue += 'orange\">Vorwarnliste</mark>'
            case 'ausgestorbenOderVerschollen':
                endangervalue += 'red\">ausgestorben oder verschollen</mark>'
            case 'vomAussterbenBedroht':
                endangervalue += 'red\">vom Aussterben bedroht</mark>'
            case 'starkGefahrdet':
                endangervalue += 'red\">stark gefährdet</mark>'
            case 'GefahrdungUnbekanntenAusmasses':
                endangervalue += 'gray\">Gefährdung unbekannten Ausmasses</mark>'
            case 'extremSelten':
                endangervalue += 'orange\">extrem selten</mark>'
            case 'DatenUnzureichend':
                endangervalue += 'gray\">Daten unzureichend</mark>'
            case 'ungefahrdet':
                endangervalue += 'green\">nicht gefährdet</mark>'
            case 'nichtBewertet':
                endangervalue += 'gray\">nicht bewertet</mark>'
            case 'keinNachweis':
                endangervalue += 'gray\">kein Nachweis</mark>'
            case _:
                return None
        return mark_safe(endangervalue)


def mini_artportrait(request, species):
    language = translation.get_language()
    return render(request, "web/mini-portrait.html", {
        "species": species,
        "species_name": species.engname if language == "en" else species.gername,
        "dark": True,
        "wikipedia": f"https://en.wikipedia.org/wiki/{quote(species.sciname)}" if language == 'en' else f"https://de.wikipedia.org/wiki/{quote(species.sciname)}",
        "species_avatar": species.avatar_new.imagefile.image.url if species.avatar_new else None
    })


def portrait(request, id):
    language = translation.get_language()

    try:
        species = Species.objects.get(id=id)
    except Species.DoesNotExist:
        raise Http404()

    fauna = is_fauna(species)
    objects = Faunaportrait.objects if fauna else Floraportrait.objects

    try:
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
    except:
        if language == 'dels':
            return redirect_dels_index()

        return mini_artportrait(request, species)

    descriptions = [portrait.short_description, portrait.male_description, portrait.female_description,
                    portrait.juvenile_description] if fauna else [portrait.short_description,
                                                                  portrait.leaf_description,
                                                                  portrait.stem_axis_description,
                                                                  portrait.flower_description,
                                                                  portrait.fruit_description]

    image_sources = [(source_from_image(portrait.descmeta), "img-description-ref")]
    if hasattr(portrait, "inthecitymeta"):
        image_sources.append((source_from_image(portrait.inthecitymeta), "img-inTheCity-ref"))
    if hasattr(portrait, "funfactmeta"):
        image_sources.append((source_from_image(portrait.funfactmeta), "img-funFacts-ref"))
    sources = list(portrait.source_set.values_list("text", flat=True))
    translate_with_lang = partial(translate_ident, 1 if language == "en" else 0)
    sources = list(map(translate_with_lang, sources))

    goodtoknows = {}
    for gtk in portrait.goodtoknow_set.all().order_by("ordering"):
        goodtoknows.setdefault(gtk.type, []).append(markdown.markdown(gtk.fact))
    goodtoknows.setdefault("other", []).append(endangerstatus(species=portrait.species, language=language))
    additional_names = ", ".join(species.speciesname_set.filter(language=language).values_list("name", flat=True))
    similar_species = [sims(language, s) for s in portrait.similarspecies_set.all()]
    unambigousfeature = [markdown.markdown(x) for x in
                         list(portrait.unambigousfeature_set.all().values_list("description", flat=True))]

    audio = {
        "audio_title": portrait.audio_title,
        "licence": portrait.faunaportrait_audio_file.license,
        "url": portrait.faunaportrait_audio_file.audio_file.url,
        "png": f"{portrait.faunaportrait_audio_file.audio_file.url.replace("audio_files", "spectrogram_images")}.png"
    } if fauna and portrait.faunaportrait_audio_file else None

    ogs_list = default_ogs(request)
    ogs_list.append(Og("og:description", portrait.short_description))
    ogs_list.append(Og("og:title", portrait.species.engname if language == "en" else portrait.species.gername))

    desc_meta = portrait.descmeta
    if desc_meta:
        image = desc_meta.image_file.large if desc_meta.image_file.large else desc_meta.image_file.image
        ogs_list = add_image_ogs(request, ogs_list, image)

    return render(request, "web/portrait.html", context={
        "og_list": ogs_list,
        "id": id,
        "dark": True,
        "portrait": portrait,
        "descriptions": [markdown.markdown(x) for x in descriptions if x is not None],
        "inthecity": [markdown.markdown(x) for x in [portrait.city_habitat, portrait.human_interaction] if
                      x is not None],
        "goodtoknows": goodtoknows,
        "image_sources": image_sources,
        "sources": sources,
        "additional_name": additional_names,
        "similar_species": similar_species,
        "unambigousfeatures": unambigousfeature,
        "audio": audio,
        "species_name": species.engname if language == "en" else species.gername,
        "species_description": _("Beschreibung"),
        "species_inthecity": _("In der Stadt"),
        "species_goodtoknows": _("Wissenswertes"),
        "show_dels": language != 'en'
    })


def redirect_dels_index() -> HttpResponseRedirect:
    url = reverse("index")
    return redirect(f"{url}?lang=dels")


def is_fauna(
        species: Species) -> bool:
    return True if species.group.nature == 'fauna' else False


def is_audio(obs_type: str) -> bool:
    return obs_type in ["audio", "unidentifiedaudio"]


def is_image(obs_type: str) -> bool:
    return obs_type in ["image", "unidentifiedimage"]


def filter_species_by_query(species_qs, query, lang):
    if not query:
        return species_qs

    if lang and (lang == 'de' or lang == 'dels'):
        return species_qs.filter(
            Q(sciname__icontains=query) | Q(gername__icontains=query) | Q(speciesname__name__icontains=query))
    elif lang and lang == 'en':
        return species_qs.filter(
            Q(sciname__icontains=query) | Q(engname__icontains=query) | Q(speciesname__name__icontains=query))
    else:
        return species_qs.filter(
            Q(sciname__icontains=query) | Q(engname__icontains=query) | Q(gername__icontains=query) | Q(
                speciesname__name__icontains=query))


def filter_species_tags(species_qs, tags):
    if not tags:
        return species_qs
    return species_qs.filter(tag__in=tags)


def is_valid_or_raise(form):
    if not form.is_valid():
        raise BadRequest(' '.join(["{}: {}".format(k, ' '.join(v)) for k, v in form.errors.items()]))


class SpeciesSearchForm(forms.Form):
    query = forms.CharField(max_length=64, required=False)
    tag = forms.TypedMultipleChoiceField(
        coerce=int,
        empty_value=[],
        choices=[(id, id) for id in Tag.objects.all().values_list('id', flat=True)],
        required=False)
    offset = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


def search_portrait(request):
    lang = translation.get_language()
    if lang == "dels":
        return redirect_dels_index()
    form = SpeciesSearchForm(request.GET)
    is_valid_or_raise(form)
    if lang == "en":
        tags = Tag.objects.filter(species__portrait__published=True).distinct().order_by("english_name")
    else:
        tags = Tag.objects.filter(species__portrait__published=True).distinct().order_by("name")
    return render(request, "web/search_portrait.html", {
        "lang": translation.get_language(),
        "query": form.cleaned_data["query"],
        "tags": tags,
        "selected_tags": tags.filter(id__in=form.cleaned_data["tag"]),
        "dark": True,
        "show_dels": lang != 'en'
    })


def search_portrait_data(request):
    lang = translation.get_language()
    if lang == "en":
        order_by = "engname"
    else:
        order_by = "gername"
    form = SpeciesSearchForm(request.GET)
    is_valid_or_raise(form)
    query = form.cleaned_data["query"]
    tags = form.cleaned_data["tag"]
    offset = form.cleaned_data["offset"] or 0
    limit = form.cleaned_data["limit"] or 64

    species_qs = (Species.objects.select_related('avatar_new', 'group')
    .prefetch_related(
        Prefetch(
            "portrait_set", to_attr="prefetched_portraits"
        )
    ))
    species_qs = filter_species_by_query(species_qs, query, lang)
    species_qs = filter_species_tags(species_qs, tags)
    species_qs = species_qs.filter(
        Q(avatar_new__isnull=False) & Q(portrait__language=lang) & Q(portrait__published=True) & Q(
            portrait__descmeta__image_file__isnull=False))

    species = [
        (
            s.id,
            s.prefetched_portraits[0].descmeta.image_file.image_small.url,
            s.prefetched_portraits[0].descmeta.image_file.image_small.width,
            s.prefetched_portraits[0].descmeta.image_file.image_small.height,
            s.group,
            s.name(lang),
            s.sciname
        ) for s in species_qs.distinct().order_by(order_by)[offset:(offset + limit)]
    ]
    return render(request, "web/search_portrait_data.html",
                  {"species": species, "more": len(species) == limit, "lang": lang})


def mobileapp(request):
    return web_render(request, "mobileapp")


def show_map(request):
    longitude = request.GET.get("lng", 13.3792)
    latitude = request.GET.get("lat", 52.5295)
    zoom = request.GET.get("zoomLevel", 9)
    return web_render(request, "map", context={
        "MAP_BOX_KEY": os.getenv('MAP_BOX_KEY'),
        "longitude": longitude,
        "latitude": latitude,
        "zoom": zoom
    })


def faq(request):
    return web_render(request, "faq")


def kontakt(request):
    return web_render(request, "contact")


def privacy(request):
    return web_render(request, "privacy")


def imprint(request):
    return web_render(request, "imprint")


def delsbedienung(request):
    return web_render(request, "delsbedienung")


def naturespots(request):
    longitude = request.GET.get("lng", 13.3792)
    latitude = request.GET.get("lat", 52.5295)
    zoom = request.GET.get("zoomLevel", 9)

    return render(request, "web/naturespots.html", context={
        "longitude": longitude,
        "latitude": latitude,
        "zoom": zoom
    })


DELS_TO_DE_FALLBACKS = ['imprint', 'digitalaccessibilitystatement']


def web_render(request, template: str, context={}) -> HttpResponse:
    language = translation.get_language()
    context["language"] = language
    context["show_dels"] = language != 'en'

    try:
        get_template(f"web/{template}.{language}.html")
        return render(request, f"web/{template}.{language}.html", context)
    except TemplateDoesNotExist:
        if template in DELS_TO_DE_FALLBACKS and language == 'dels':
            return render(request, f"web/{template}.de.html", context)
        elif language == 'dels':
            return redirect_dels_index()
        else:
            raise Http404()


def digitalaccessibilitystatement(request):
    return web_render(request, "digitalaccessibilitystatement")


def default_ogs(request: WSGIRequest) -> list[Og]:
    return [Og("og:type", "website"),
            Og("og:site-name", "Naturblick"),
            Og("og:url", og_url(request))
            ]


def og_url(request):
    return f'{request.get_host()}{request.get_full_path().replace("/index", "")}'


def seen_by(obs_type, user, date):
    if is_audio(obs_type):
        return _("Gehört von {user} {when} in __PLACE__").format(user=user,
                                                                 when=from_time(datetime.now(timezone.utc), date))
    else:
        return _("Gesehen von {user} {when} in __PLACE__").format(user=user,
                                                                  when=from_time(datetime.now(timezone.utc), date))


def add_image_ogs(request, ogs_list, image):
    ogs_list.append(Og("og:image:width", image.width))
    ogs_list.append(Og("og:image:height", image.height))
    ogs_list.append(Og("og:image", f'{request.get_host()}{image.url}'))
    ogs_list.append(Og("og:twitter:image", f'{request.get_host()}{image.url}'))
    return ogs_list


def to_geojson_view(source):
    features = []

    for row in source["data"]:
        obj_id, lon, lat, kind = row

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat],
            },
            "properties": {
                "id": obj_id,
                "group": kind
            }
        }

        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return JsonResponse(geojson)


def map_proxy(request):
    r = requests.get(
        f"{settings.PLAYBACK_URL}projects/map"
    )
    return to_geojson_view(r.json())


def geo_proxy(request):
    return JsonResponse(requests.get(
        f"{settings.PLAYBACK_URL}naturespots"
    ).json())


def naturespot_proxy(request, id):
    return JsonResponse(requests.get(
        f"{settings.PLAYBACK_URL}naturespots"
    ).json())


def naturespotportrait(request, id):
    language = translation.get_language()
    ids_json = requests.get(f"{settings.PLAYBACK_URL}naturespots/{id}".format(id=id)).json()

    name_field = "gername"
    if language == 'en':
        "engname"

    data = [{"name": v[0], "sciname": v[1], "pid": v[2]} for v in Species.objects.filter(
        id__in=ids_json["ids"],
        portrait__language=language
    ).order_by(name_field).values_list(
        name_field,
        "sciname",
        "portrait__species_id"  # we want to know whether there is an artportrait of this species or not
    )]

    schutzstatus = ""
    match ids_json["schutzstatus"]:
        case 'a_nd':
            schutzstatus = _("Naturdenkmal")
        case 'b_spa':
            schutzstatus = _("Special protected area")
        case 'c_ffh':
            schutzstatus = _("Fauna-Flora-Habitat")
        case 'd_np':
            schutzstatus = _("Naturpark")
        case 'e_fnd':
            schutzstatus = _("Naturdenkmale Bäume und Findlinge")
        case 'f_fspr':
            schutzstatus = _("Flächen mit spezieller Regelung")
        case 'g_glb':
            schutzstatus = _("geschützter Landschaftsbestandteil")
        case 'h_nsg':
            schutzstatus = _("Naturschutzgebiet")
        case 'i_lsg':
            schutzstatus = _("Landschaftsschutzgebiet")
        case 'j_br':
            schutzstatus = _("Biosphärenreservat")
        case 'k_natp':
            schutzstatus = _("Nationalpark")

    return web_render(request, "naturespotportrait", {
        "id": id,
        "name": ids_json["name"],
        "schutzstatus": schutzstatus,
        "data": data
    }
                      )


def obs(request, obs_id):
    language = translation.get_language()
    data = response_json(requests.get(f"{settings.PLAYBACK_URL}projects/observations/{obs_id}")).get("data")
    species_id = data["species"]
    s = Species.objects.filter(id=species_id).first()
    obs_type = data["obsType"]
    cc_name = data["ccName"]
    date_time = datetime.fromisoformat(data["dateTime"])
    date = date_time.strftime("%d.%m.%Y")
    coords = data["coords"]["coordinates"]
    additional_names = ", ".join(
        s.speciesname_set.filter(language=language).values_list("name", flat=True))

    obs_data = {
        "obs_id": obs_id,
        "sciname": s.sciname,
        "name": s.engname if language == 'en' else s.gername,
        "additional_names": additional_names,
        "coords": coords,
        "cc_name": cc_name,
        "species_avatar": s.avatar_new.imagefile.image.url,
        "is_image": is_image(obs_type),
        "is_audio": is_audio(obs_type),
        "language": language
    }

    if is_fauna(s):
        obs_data["portrait_audio_url"] = Faunaportrait.objects.filter(
            species=species_id).first().faunaportrait_audio_file.audio_file.url

    if is_audio(obs_type):
        obs_data["png_url"] = f"/api/projects/observations/{obs_id}/audio.mp4.png"
        obs_data["mp4_url"] = f"/api/projects/observations/{obs_id}/audio.mp4"
    elif is_image(obs_type):
        obs_data["jpg_url"] = f"/api/projects/observations/{obs_id}/image.jpg"

    return render(request, "partials/obs_popup.html", {
        "obs_data": obs_data,
        "title": seen_by(obs_type, cc_name, date_time),
        "species_has_audio": "portrait_audio_url" in obs_data
    })


def nightingaleproject(request):
    return web_render(request, "nightingaleproject")


def plausibility(within_timeframe, within_range):
    if within_timeframe and within_range:
        return _("Diese Beobachtung ist plausibel.")
    elif within_timeframe or within_range:
        return _("Diese Beobachtung ist teilweise plausibel.")
    else:
        return _("Diese Beobachtung ist nicht plausibel.")


def assessment_text(assessment):
    if assessment is None:
        return _("Es hat noch kein:e Expert:in die Beobachtung angesehen.")
    elif assessment == "true":
        return _("Ein:e Expert:in konnte die Bestimmung bestätigen.")
    elif assessment == "uncertain_true":
        return _(
            "Ein:e Expert:in konnte die Artbestimmung nicht sicher bestätigen, hält sie aber für wahrscheinlich richtig.")
    elif assessment == "uncertain_false":
        return _(
            "Ein:e Expert:in konnte die Artbestimmung nicht sicher ausschließen, hält sie aber für wahrscheinlich falsch.")
    elif assessment == "impossible":
        return _("Ein:e Expert:in ist sich nach Sichtung des Mediums nicht sicher.")
    else:
        raise ValueError(f"Unexpected assessment value: {assessment}")


def species_matching_score(species, score):
    return {
        "name": species.engname if translation.get_language() == "en" else species.gername,
        "sciname": species.sciname,
        "score": score
    }


def confirmation(assessment, pattern_matching_executed, pattern_matching_confirmed, pattern_matching_medium) -> str:
    if assessment is None:
        if pattern_matching_confirmed:
            return _("Dieser Artzuordnung wurde teilweise zugestimmt.")
        elif not pattern_matching_executed:
            return _("Diese Artzuordnung wurde noch nicht angesehen.")
        else:
            return _("Diese Artzuordnung kann nicht sicher eingeschätzt werden.")

    elif assessment == "true":
        if (
                pattern_matching_confirmed
                or pattern_matching_medium
        ):
            return _("Dieser Artzuordnung wurde zugestimmt.")
        else:
            return _("Dieser Artzuordnung wurde teilweise zugestimmt.")

    elif assessment in ("uncertain_true", "uncertain_false", "impossible"):
        if pattern_matching_confirmed:
            return _("Dieser Artzuordnung wurde teilweise zugestimmt.")
        else:
            return _("Diese Artzuordnung kann nicht sicher eingeschätzt werden.")
    return _("Dieser Artzuordnung wurde zugestimmt.")


def map_obs(request, obs_id):
    language = translation.get_language()
    if language == 'dels':
        return redirect_dels_index()
    data = response_json(
        requests.get(f"{settings.PLAYBACK_URL}projects/observations/{obs_id}")
    ).get("data")
    species_id = data.get("species")
    species = Species.objects.filter(id=species_id).first()
    cc_name = data.get("ccName")
    obs_type = data.get("obsType")
    date_time = datetime.fromisoformat(data.get("dateTime"))
    coords = data.get("coords").get("coordinates")

    fauna = is_fauna(species)
    objects = Faunaportrait.objects if fauna else Floraportrait.objects
    additional_names = ", ".join(
        species.speciesname_set.filter(language=language).values_list("name", flat=True))

    within_range = data.get("withinRange")
    within_timeframe = data.get("withinTimeframe")
    plausibility_author_id = data.get("plausibilityAuthor")
    pattern_matching_executed = data.get("patternMatchingExecuted")

    is_forschungsfall_nachtigall = True if len(data.get("projects")) > 0 and data.get("projects")[0] == 1 else False

    assessment_author_id = data.get("assessmentAuthor")
    assessment = data.get("assessment")
    suggested_species = data.get("suggestedSpecies")  # [['bird_...', 99], [...], [...] ]

    pattern_matching_confirmed = suggested_species[0][0] == species.speciesid if suggested_species and len(
        suggested_species) > 0 else False
    pattern_matching_medium = suggested_species[1][0] == species.speciesid if suggested_species and len(
        suggested_species) > 1 else False

    matched_species = []
    if suggested_species:
        matched_species = [species_matching_score(Species.objects.filter(speciesid=s[0]).first(), round(s[1]))
                           for s in suggested_species
                           ]

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
        .get(species_id=species.id, language=language)
    )

    p_author = EvaluationAuthor.objects.get(id=plausibility_author_id)
    plausibility_author_text = f"{p_author.name}, {p_author.institution}"

    pattern_matching_text = pattern_matching(pattern_matching_confirmed, pattern_matching_executed,
                                             pattern_matching_medium, species)

    a_author = EvaluationAuthor.objects.get(id=assessment_author_id) if assessment_author_id else None
    assessment_author_text = f"{a_author.name}, {a_author.institution}" if a_author else None
    confirmation_text = confirmation(assessment, pattern_matching_executed, pattern_matching_confirmed,
                                     pattern_matching_medium) if assessment else None

    context = {
        "obs_id": obs_id,
        "group": species.group,
        "cc_name": cc_name,
        "locale": translation.get_language(),
        "date_time": date_time,
        "name": species.engname if language == 'en' else species.gername,
        "sciname": species.sciname,
        "species_avatar": species.avatar_new.imagefile.image.url,
        "species_id": species.id,
        "portrait_audio_url": portrait.faunaportrait_audio_file.audio_file.url if fauna else None,
        "is_fauna": fauna,
        "additional_names": additional_names,
        "seen_by": seen_by(obs_type, cc_name, date_time),
        "within_range": _("Sie liegt im Verbreitungsgebiet.") if within_range else _(
            "Sie liegt nicht im Verbreitungsgebiet."),
        "plausibility": plausibility(within_timeframe, within_range),
        "within_timeframe": _("Sie wurde im Aktivitätszeitraum gemacht.") if within_timeframe else _(
            "Sie wurde nicht im Aktivitätszeitraum gemacht."),
        "plausibility_author_text": plausibility_author_text,
        "assessment_author_text": assessment_author_text,
        "coords": coords,
        "assessment_text": assessment_text(assessment),
        "assessment": assessment,
        "matched_species": matched_species,
        "pattern_matching_confirmed": pattern_matching_confirmed,
        "pattern_matching_medium": pattern_matching_medium,
        "pattern_matching_text": pattern_matching_text,
        "pattern_matching_executed": pattern_matching_executed,
        "is_forschungsfall_nachtigall": is_forschungsfall_nachtigall,
        "confirmation_text": confirmation_text,
        "individuals": data.get("individuals"),
        "MAP_BOX_KEY": os.getenv('MAP_BOX_KEY'),
        "dark": True
    }

    if fauna:
        context["png_url"] = f"/api/projects/observations/{obs_id}/audio.mp4.png"
        context["mp4_url"] = f"/api/projects/observations/{obs_id}/audio.mp4"
    else:
        context["jpg_url"] = f"/api/projects/observations/{obs_id}/image.jpg"

    context["language"] = language
    context["show_dels"] = language != 'en'

    # ogs

    ogs_list = []

    try:
        species_id = data["species"]
        s = Species.objects.filter(id=species_id).first()
        cc_name = data["ccName"]
        date_time = datetime.fromisoformat(data["dateTime"])

        ogs_list.append(Og("og:title", s.engname if language == "en" else s.gername))

        obs_type = data["obsType"]
        if is_image(obs_type):
            ogs_list.append(Og("og:image",
                               f"https://naturblick.museumfuernaturkunde.berlin/api/projects/observations/{obs_id}/image.jpg"))
            ogs_list.append(Og("og:twitter:image",
                               f"https://naturblick.museumfuernaturkunde.berlin/api/projects/observations/{obs_id}/image.jpg"))
        elif is_audio(obs_type):
            ogs_list.append(Og("og:audio",
                               f"https://naturblick.museumfuernaturkunde.berlin/api/projects/observations/{obs_id}/audio.mp4"))

        ogs_list.append(Og("og:description", seen_by(fauna, cc_name, date_time)))
    except:
        pass

    context["og_list"] = ogs_list

    return render(request, f"web/obs_detail.html", context)


def pattern_matching(pattern_matching_confirmed, pattern_matching_executed,
                     pattern_matching_medium, species) -> str:
    if not pattern_matching_executed:
        pattern_matching_text = _("Es wurde keine Mustererkennung durchgeführt.")
    else:
        if pattern_matching_confirmed:
            pattern_matching_text = species.engname if translation.get_language() == "en" else species.gername + _(
                " hatte die größte Übereinstimmung mit dem trainierten Vergleichsmaterial der Mustererkennung.")
        elif pattern_matching_medium:
            pattern_matching_text = _(
                "Die Art war unter den drei Arten mit der größten Übereinstimmung mit dem trainierten Vergleichsmaterial der Mustererkennung.")
        else:
            pattern_matching_text = _(
                "Die Art war nicht unter den drei Arten mit der größten Übereinstimmung mit dem trainierten Vergleichsmaterial der Mustererkennung.")
    return pattern_matching_text


def plantrecognition(request):
    return web_render(request, "plantrecognition", context={
        "species_list": requests.get(f"{settings.PLAYBACK_URL}imageidspecies").json(),
        "lang": translation.get_language()
    })


def animalrecognition(request):
    return web_render(request, "animalrecognition", context={
        "species_list": requests.get(f"{settings.PLAYBACK_URL}soundidspecies").json(),
        "lang": translation.get_language()
    })


def speciesimagerecognition(request):
    return web_render(request, "speciesimagerecognition")


def speciesaudiorecognition(request):
    return web_render(request, "speciesaudiorecognition")

class ViewResultsForm(forms.Form):
    device_identifier = forms.CharField(label="Device identifier", max_length=100)

@login_required(login_url='/admin/login/')
def plantnetdemo(request):

    if request.method == "POST":
        form = ViewResultsForm(request.POST)
        if form.is_valid():
            request.session['device_identifier'] = form.cleaned_data['device_identifier']
            observations = requests.put(
                f"{settings.PLAYBACK_URL}obs/androidsync",
                files= {'operations': (None, json.dumps({"operations": [], "syncInfo": {"deviceIdentifier": request.session['device_identifier']}}))},
                headers={'X-MfN-Device-Id': request.session['device_identifier']}
            ).json()['data']
            image_observations = [o for o in observations if o['obsType'] == 'image']
    else:
        form = ViewResultsForm()
        image_observations = None
        try:
            del request.session['device_identifier']
        except:
            pass
    return render(
            request,
            "web/plantnetdemo.html",
            context={
                "form": form,
                "observations": image_observations
        })

@login_required(login_url='/admin/login/')
def plantnetresults(request, thumbnail_id):
    plantnet_data = requests.get(f"{settings.PLAYBACK_URL}highertaxonsimageid?mediaId={thumbnail_id}").json()
    return render(
        request,
        "web/plantnetresults.html",
        context={
            "thumbnail_id": thumbnail_id,
            "pn": plantnet_data
        })

@login_required(login_url='/admin/login/')
def plantnetimg(request, thumbnail_id):
    url = f"https://naturblick.museumfuernaturkunde.berlin/api/media/{thumbnail_id}"
    r = requests.get(url, stream=True, headers={'X-MfN-Device-Id': request.session['device_identifier']})

    r.raise_for_status()
    
    return HttpResponse(
        r.iter_content(chunk_size=8192),
        content_type=r.headers.get("Content-Type", "image/jpeg")
    )

