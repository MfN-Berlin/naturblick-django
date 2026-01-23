from django.urls import path, re_path

from web import views

urlpatterns = [
    path('', views.home),
    re_path(
        r'^species/portrait[^/]*/(?P<id>[0-9]+)/?$', views.artportrait, name="artportrait"),
    re_path(
        r'^species/portrait[^/]*/(?P<species_id>[a-z]+_[a-f0-9]{8})/?$', views.old_artportrait),
    path('map/observation/<int:obs_id>', views.map_page),
    re_path(r'^\w+(?:/\w+){0,1}$', views.sub_page),
    re_path(r'^species/.*$', views.default_response),
]
