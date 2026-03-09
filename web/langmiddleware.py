from django.core.exceptions import BadRequest
from django.utils import translation

def set_lang_middleware(get_response):
    availble_langs = [ "de", "en", "dels"]

    def middleware(request):
        lang = request.GET.get('lang') if request.GET.get('lang') else "de"
        if lang not in availble_langs:
            raise BadRequest("Language not available")
        translation.activate(lang)
        response = get_response(request)

        return response

    return middleware
