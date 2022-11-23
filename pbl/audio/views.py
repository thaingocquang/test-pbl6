from django.shortcuts import render
from .forms import AudioForm
from django.http import HttpResponse
from django.core.files.storage import default_storage
import os
from django.conf import settings
from django.core.files.base import ContentFile
import glob
from typing import List, Dict, Tuple
from tqdm import tqdm
import pickle
from scipy.io.wavfile import read
from .handlewav.constellation import create_constellation
from .handlewav.hash import create_hashes
import pickle

def audio_store(request):
    if request.method == 'POST':
        form = AudioForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
            return HttpResponse('successfully upload')
    else:
        form = AudioForm()
    return render(request, 'aud.html', {'form': form})


def song_to_pickle(request):
    path = "pbl/media/"
    songs = glob.glob(path + 'documents/*.wav')

    song_name_index = {}
    database: Dict[int, List[Tuple[int, int]]] = {}

    # Go through each song, using where they are alphabetically as an id
    for index, filename in enumerate(tqdm(sorted(songs))):
        print('filename', filename)

        song_name_index[index] = filename
        # Read the song, create a constellation and hashes
        Fs, audio_input = read(filename)
        constellation = create_constellation(audio_input, Fs)
        hashes = create_hashes(constellation, index)

        # For each hash, append it to the list for this hash
        for hash, time_index_pair in hashes.items():
            if hash not in database:
                database[hash] = []
            database[hash].append(time_index_pair)
    # Dump the database and list of songs as pickles
    with open("database/database.pickle", 'wb') as db:
        pickle.dump(database, db, pickle.HIGHEST_PROTOCOL)
    with open("database/song_index.pickle", 'wb') as songs:
        pickle.dump(song_name_index, songs, pickle.HIGHEST_PROTOCOL)

    return HttpResponse('ok')


def song_recognition(request):
    if request.method == 'POST':
        form = AudioForm(request.POST, request.FILES or None)
        path = default_storage.save('tmp/somename.wav', ContentFile(request.FILES.get('record').read()))

        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        # print('tmp_file', tmp_file)

        if form.is_valid() == False:
            return HttpResponse('Song to recognition upload failed!')

        # Load the database
        database = pickle.load(open('database/database.pickle', 'rb'))
        song_name_index = pickle.load(open("database/song_index.pickle", "rb"))

        # Load a short  recording with some backgroundnoise
        Fs, audio_input = read(tmp_file)

        # Create the constellation and hashes
        constellation = create_constellation(audio_input, Fs)
        hashes = create_hashes(constellation, None)

        # For each hash in the song, check if there's a match in the database
        # There could be multiple matching tracks, so for each match:
        #   Incrememnt a counter for that song ID by one
        matches_per_song = {}
        for hash, (sample_time, _) in hashes.items():
            if hash in database:
                matching_occurences = database[hash]
                for source_time, song_id in matching_occurences:
                    if song_id not in matches_per_song:
                        matches_per_song[song_id] = 0
                    matches_per_song[song_id] += 1

        res = ''
        for song_id, num_matches in list(sorted(matches_per_song.items(), key=lambda x: x[1], reverse=True))[:10]:
            res += "Song: " + str(song_name_index[song_id]) + " - Matches " + str(num_matches) + "\n\n"
            # print(f"Song: {song_name_index[song_id]} - Matches: {num_matches}")


        return HttpResponse(res, content_type="text/plain")
    else:
        form = AudioForm()
    return render(request, 'recog.html', {'form': form})


import pathlib


def list_song(request):
    path =str(pathlib.Path().resolve())  + '/media/documents/*.wav'
    songs = glob.glob(path)
    res = ''
    for index, filename in enumerate(tqdm(sorted(songs))):
        res += filename + '\n'
    return HttpResponse(res, content_type="text/plain")