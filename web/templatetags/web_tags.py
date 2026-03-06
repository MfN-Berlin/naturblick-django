from django import template
from django.contrib.staticfiles import finders
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.templatetags.static import static


register = template.Library()

@register.simple_tag
def toggle_lang(request):
    params = request.GET.copy()
    current = params.get("lang", "de")

    params["lang"] = "en" if current == "de" else "de"

    query = params.urlencode()
    return f"{request.path}?{query}" if query else request.path

@register.simple_tag
def toggle_dels(request):
    params = request.GET.copy()
    current = params.get("lang", "de")

    params["lang"] = "dels" if current == "de" else "de"

    query = params.urlencode()
    return f"{request.path}?{query}" if query else request.path

@register.simple_tag
def inline_svg(path):
    full_path = finders.find(path)
    if full_path:
        with open(full_path, 'r', encoding='utf-8') as f:
            return mark_safe(f.read())
    return ''

@register.simple_tag
def group_svg(group):
    match group.name:
        case "reptile": path = "reptilien.svg"
        case "mammal": path = "mammal.svg"
        case "butterfly": path = "butterfly.svg"
        case "conifer": path = "nadelbaueme.svg"
        case "amphibian": path = "amphibian.svg"
        case "hymenoptera": path = "bee.svg"
        case "herb": path = "herb.svg"
        case "bird": path = "bird.svg"
        case "tree": path = "tree.svg"
        case "fishingbaitfish": path = "fishing-bait-fish.svg"
        case "actinopterygii": path = "fishing-bait-fish.svg"
        case "chondrichthyes": path = "fishing-bait-fish.svg"
        case "insectcentipede": path = "insect-centipede.svg"
        case "chilopoda": path = "insect-centipede.svg"
        case "diplopoda": path = "insect-centipede.svg"
        case "snail": path = "snail.svg"
        case "anaspidea": path = "snail.svg"
        case "bivalvia": path = "snail.svg"
        case "cephalaspidea": path = "snail.svg"
        case "cephalopoda": path = "snail.svg"
        case "gastropoda": path = "snail.svg"
        case "spider": path = "spider.svg"
        case "acarida": path = "spider.svg"
        case "arachnid": path = "spider.svg"
        case "araneae": path = "spider.svg"
        case "hydrachnidia": path = "spider.svg"
        case "shellfishcrab": path = "shellfish-crab.svg"
        case "amphipoda": path = "shellfish-crab.svg"
        case "branchiopoda": path = "shellfish-crab.svg"
        case "crustacea": path = "shellfish-crab.svg"
        case "maxillopoda": path = "shellfish-crab.svg"
        case "insectant": path = "insect-ant.svg"
        case "blattodea": path = "insect-ant.svg"
        case "bug": path = "insect-ant.svg"
        case "coleoptera": path = "insect-ant.svg"
        case "dermaptera": path = "insect-ant.svg"
        case "diptera": path = "insect-ant.svg"
        case "ephemeroptera": path = "insect-ant.svg"
        case "grasshopper": path = "insect-ant.svg"
        case "heteroptera": path = "insect-ant.svg"
        case "lepidoptera": path = "insect-ant.svg"
        case "mantodea": path = "insect-ant.svg"
        case "mecoptera": path = "insect-ant.svg"
        case "megaloptera": path = "insect-ant.svg"
        case "neuroptera": path = "insect-ant.svg"
        case "odonata": path = "insect-ant.svg"
        case "planipennia": path = "insect-ant.svg"
        case "plecoptera": path = "insect-ant.svg"
        case "psocoptera": path = "insect-ant.svg"
        case "raphidioptera": path = "insect-ant.svg"
        case "thysanoptera": path = "insect-ant.svg"
        case "trichoptera": path = "insect-ant.svg"
        case "truebug": path = "insect-ant.svg"
        case "zygentoma": path = "insect-ant.svg"
        case "all": path = "all.svg"
        case _: "logo.svg"

    full_path = finders.find(f"groups/{path}")
    if full_path:
        with open(full_path, 'r', encoding='utf-8') as f:
            return mark_safe(f.read())
    return ''


@register.simple_tag
def img(path, widths, sizes):  #
    root = 'web/img/'
    prefixes = ['thumbnail', 'small', 'medium', 'large']
    src = static(root + path)
    srcset = ''
    widths = widths.split(',')

    for index, w in enumerate(widths):
        srcset_path = static(f'{root}{prefixes[index]}_{path}')
        srcset += f'{srcset_path} {w}, '
    srcset += src

    return format_html(
        '<img src="{}" srcset="{}" sizes="{}" loading="lazy">',
        src,
        srcset,
        sizes
    )