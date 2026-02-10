from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe

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