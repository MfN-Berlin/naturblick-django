from django.urls import path, re_path

from apiproxy import views

urlpatterns = [
    path("projects/observations/<int:obs_id>/audio.mp4", views.audio_proxy, name="audio_proxy"),
    path("projects/observations/<int:obs_id>/audio.mp4.png", views.specgram_proxy, name="specgram_proxy"),
    path("projects/observations/<int:obs_id>/image.jpg", views.image_proxy, name="image_proxy"),
]
