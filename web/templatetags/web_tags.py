from django import template

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