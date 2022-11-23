from django.urls import path
from .views import audio_store, song_to_pickle, song_recognition, list_song

urlpatterns = [
    path('', audio_store),
    path('song-to-pickle', song_to_pickle),
    path('song-recognition', song_recognition),
    path('list-song', list_song),
]