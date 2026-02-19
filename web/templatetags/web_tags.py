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