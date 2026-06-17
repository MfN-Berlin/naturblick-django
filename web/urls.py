from django.urls import path, re_path

from web import views

urlpatterns = [
    path("", views.index, name="index"),
    path("communities/nightingaleproject", views.nightingaleproject, name="nightingaleproject"),
    path("map/observation/<int:obs_id>", views.map_obs, name="map_obs"),
    path("map_proxy", views.map_proxy, name="map_proxy"),
    path("geo_proxy", views.geo_proxy, name="geo_proxy"),
    path("obs/<int:obs_id>", views.obs, name="obs"),
    path("species/portrait/data", views.search_portrait_data, name="search_portrait_data"),
    re_path(
        r'^species/portrait/(?P<id>[0-9]+)$', views.portrait, name="portrait"),
    path("species/portrait;view=grid", views.search_portrait),
    path("species/portrait", views.search_portrait, name="search_portrait"),
    path("faq", views.faq, name="faq"),
    path("mobileapp", views.mobileapp, name="mobileapp"),
    path("about", views.about, name="about"),
    path("kontakt", views.kontakt, name="kontakt"),
    path("privacy", views.privacy, name="privacy"),
    path("imprint", views.imprint, name="imprint"),
    path("delsbedienung", views.delsbedienung, name="delsbedienung"),
    path("naturespots", views.naturespots, name="naturespots"),
    path("naturespot/<int:id>", views.naturespotportrait, name="naturespotportrait"),
    path("map", views.show_map, name="map"),
    path("digitalaccessibilitystatement", views.digitalaccessibilitystatement, name="digitalaccessibilitystatement"),
    path("plantrecognition", views.plantrecognition, name="plantrecognition"),
    path("animalrecognition", views.animalrecognition, name="animalrecognition"),
    path("speciesimagerecognition", views.speciesimagerecognition, name="speciesimagerecognition"),
    path("speciesaudiorecognition", views.speciesaudiorecognition, name="speciesaudiorecognition"),
    re_path(
        r'^species/portrait[^/]*/(?P<species_id>[a-z]+_[a-f0-9]{8})/?$', views.old_artportrait),
    path('plantnetdemo', views.plantnetdemo, name="plantnetdemo"),
    path('plantnetdemo/<uuid:thumbnail_id>', views.plantnetresults, name="plantnetresults"),
    path('plantnetdemo/<uuid:thumbnail_id>.jpeg', views.plantnetimg, name="plantnetimg"),
    path('naturblick-leicht-ci', views.nb_leicht_ci, name='nb_leicht_ci')
]
