from django.utils import translation

def set_lang_middleware(get_response):

    def middleware(request):
        lang = request.GET.get('lang') if request.GET.get('lang') else "de"
        translation.activate(lang)
        response = get_response(request)

        return response

    return middleware