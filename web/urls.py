from django.urls import path, re_path

from web import views

urlpatterns = [
    path("dev", views.index, name="index"),
    path("dev/communities/nightingaleproject", views.nightingaleproject, name="nightingaleproject"),
    path("dev/map/observation/<int:obs_id>", views.map_obs, name="map_obs"),
    path("dev/map_proxy", views.map_proxy, name="map_proxy"),
    path("dev/audio_proxy/<int:obs_id>", views.audio_proxy, name="audio_proxy"),
    path("dev/specgram_proxy/<int:obs_id>", views.specgram_proxy, name="specgram_proxy"),
    path("dev/image_proxy/<int:obs_id>", views.image_proxy, name="image_proxy"),
    path("dev/obs/<int:obs_id>", views.obs, name="obs"),
    path("dev/species/portrait;view=grid", views.search_portrait, name="search_portrait"),
    path("dev/species/portrait/data", views.search_portrait_data, name="search_portrait_data"),
    re_path(
        r'^dev/species/portrait/(?P<id>[0-9]+)$', views.portrait, name="portrait"),
    path("dev/faq", views.faq, name="faq"),
    path("dev/mobileapp", views.mobileapp, name="mobileapp"),
    path("dev/about", views.about, name="about"),
    path("dev/kontakt", views.kontakt, name="kontakt"),
    path("dev/privacy", views.privacy, name="privacy"),
    path("dev/imprint", views.imprint, name="imprint"),
    path("dev/map", views.show_map, name="map"),
    path("dev/digitalaccessibilitystatement", views.digitalaccessibilitystatement, name="digitalaccessibilitystatement"),
    path('', views.home, name="home"),
    re_path(
        r'^species/portrait[^/]*/(?P<id>[0-9]+)/?$', views.artportrait, name="artportrait"),
    re_path(
        r'^species/portrait[^/]*/(?P<species_id>[a-z]+_[a-f0-9]{8})/?$', views.old_artportrait),
    path('map/observation/<int:obs_id>', views.map_page),
    re_path(r'^species/.*$', views.default_response),
    re_path(r'^.*$', views.sub_page), # Match anything and let Angular handle 404
]
