from django.utils.translation import gettext as _
from django.http import Http404
from requests.exceptions import HTTPError

def from_time(now, time):
    delta = now - time
    months = round(delta.days / 30.44)
    years = round(delta.days / 365.25)

    if months > 11:
        if years > 1:
            return _("vor {years} Jahren").format(years=years)
        else:
            return _("vor einem Jahr")
    elif months > 1:
        return _("vor {months} Monaten").format(months=months)
    else:
        return  _("neulich")

def response_json(response):
    try:
        response.raise_for_status()
        return response.json()
    except HTTPError:
        if response.status_code == 404:
            raise Http404()
        raise
