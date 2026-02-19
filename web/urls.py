from django.urls import path, re_path

from web import views

urlpatterns = [
    path("dev", views.index, name="index"),
    path("dev/faq", views.faq, name="faq"),
    path("dev/mobileapp", views.mobileapp, name="mobileapp"),
    path("dev/about", views.about, name="about"),
    path("dev/kontakt", views.kontakt, name="kontakt"),
    path("dev/privacy", views.privacy, name="privacy"),
    path("dev/imprint", views.imprint, name="imprint"),
    path("dev/digitalaccessibilitystatement", views.digitalaccessibilitystatement, name="digitalaccessibilitystatement"),
    path('', views.home, name="home"),
    re_path(
        r'^species/portrait[^/]*/(?P<id>[0-9]+)/?$', views.artportrait, name="artportrait"),
    re_path(
        r'^species/portrait[^/]*/(?P<species_id>[a-z]+_[a-f0-9]{8})/?$', views.old_artportrait),
    path('map/observation/<int:obs_id>', views.map_page),
    re_path(r'^\w+(?:/\w+){0,1}$', views.sub_page),
    re_path(r'^species/.*$', views.default_response),
    ]
