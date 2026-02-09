from django.urls import path, re_path

from web import views

urlpatterns = [
    path("faq", views.faq, name="faq"),
    path("mobileapp", views.mobileapp, name="mobileapp"),
    path("about", views.about, name="about"),
    path("kontakt", views.kontakt, name="kontakt"),
    path("privacy", views.privacy, name="privacy"),
    path("imprint", views.imprint, name="imprint"),
    path("digitalaccessibilitystatement", views.digitalaccessibilitystatement, name="digitalaccessibilitystatement"),
    path('', views.home, name="home"),
    re_path(
        r'^species/portrait[^/]*/(?P<id>[0-9]+)/?$', views.artportrait, name="artportrait"),
    re_path(
        r'^species/portrait[^/]*/(?P<species_id>[a-z]+_[a-f0-9]{8})/?$', views.old_artportrait),
    path('map/observation/<int:obs_id>', views.map_page),
    re_path(r'^\w+(?:/\w+){0,1}$', views.sub_page),
    re_path(r'^species/.*$', views.default_response),
    ]
