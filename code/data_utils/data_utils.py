import collections
import datetime
import functools
import json
import os
import pickle
import pylab
import random

import utils.hdf5_getters as hdf5_getters
import utils.metrics as metrics
from utils.time_logger import log_time_spent

# defines data location in repository structure
def get_data_path():
    data_path = os.path.realpath("../data")
    return data_path

#---------------------------------------------------------------------------------------------------
# JSON manipulation utilities

#Encoder taken from http://stackoverflow.com/questions/8230315/python-sets-are-not-json-serializable
class PythonObjectEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (list, dict, str, unicode, int, float, bool, type(None))):
            return json.JSONEncoder.default(self, obj)
        return {'_python_object': pickle.dumps(obj)}


def _as_python_object(dct):
    if '_python_object' in dct:
        return pickle.loads(str(dct['_python_object']))
    return dct


def save_json(json_dict, location=None):
    if not location:
        raise ValueError("You should provide the location where to save the file")
    with open(os.path.join(get_data_path(), location), "w") as json_dump_file:
        json.dump(json_dict, json_dump_file, cls=PythonObjectEncoder)
        print "\tSaved JSON at the location {}".format(location)


def load_json(location=None):
    if not location:
        raise ValueError("You should provide the location where to save the file")
    with open(os.path.join(get_data_path(), location), "r") as json_file:
        json_data = json.load(json_file, object_hook=_as_python_object)
        print "\tSuccessfully loaded JSON {}".format(location)
        return json_data

#---------------------------------------------------------------------------------------------------
# File/Data manipulation utilities
def generate_test_users(test_users_index=1):
    """
    This method generates a new set of test users
    When running the scripts for metrics calculation, I'll use the same set of users
    """
    training_data_filename = "basic_data/train_triplets.txt"
    users_to_songs_dict = users_to_songs(filename=training_data_filename)
    training_users = generate_evaluation_data(
        users_to_songs_dict,
        ratio=0.001  #1000 users
    )

    new_test_users_filename = "input/training_users_{}.json".format(test_users_index)
    if os.path.exists(os.path.join(get_data_path(), new_test_users_filename)):
        print "{} already exists. You dont want to override it"
    else:
        save_json(training_users, location=new_test_users_filename)
        print "\n\tSuccessfully generated test users training_users_{}.json".format(test_users_index)


def load_test_users(test_users_index=1):
    test_users_filename = "input/training_users_{}.json".format(test_users_index)
    if os.path.exists(os.path.join(get_data_path(), test_users_filename)):
        return load_json(location=test_users_filename)
    else:
        print "File {} does not exists yet! Generate it first".format(test_users_filename)

def _generate_songs_to_users_json():
    songs_to_users_dict = songs_to_users()
    save_json(songs_to_users_dict, location="input/songs_to_users.json")
    print "\tSuccessfully generated songs_to_users.json"


def _convert_train_triplets_to_indexes():
    user_index = 0
    song_index = 0
    user_to_index = {}
    song_to_index = {}
    train_triplets_filename = "basic_data/train_triplets_with_original_ids.txt"
    dest_train_triplets_filename = "basic_data/train_triplets_with_indexes.txt"
    output_file = open(os.path.join(get_data_path(), dest_train_triplets_filename),"w")
    with open(os.path.join(get_data_path(), train_triplets_filename)) as input_file:
        for line in input_file:
            user_id, song_id, play_count = line.split()
            if user_id not in user_to_index:
                user_to_index[user_id] = user_index
                user_index += 1
            if song_id not in song_to_index:
                song_to_index[song_id] = song_index
                song_index += 1
            line_contents = [str(user_to_index[user_id]), str(song_to_index[song_id]), play_count]
            line_str = " ".join(line_contents) + "\n"
            output_file.write(line_str)

    output_file.close()
    print "finished"

#---------------------------------------------------------------------------------------------------

@log_time_spent()
def generate_evaluation_data(users_to_songs, ratio=0.09):
    training_users = list()
    visible_songs_by_users = dict()
    songs_listened_by_users = dict()
    user_ids = users_to_songs.keys()

    for user_id in user_ids:
        if random.random() > ratio:
            continue
        user_songs = list(users_to_songs[user_id])
        songs_len = len(user_songs)
        random.shuffle(user_songs)
        # first half stays in the evaluation
        visible_songs_by_users[user_id] = set(user_songs[:(songs_len/2)])
        # second half goes to the really listened songs
        songs_listened_by_users[user_id] = set(user_songs[(songs_len/2):])
        training_users.append(dict(
            user_id=user_id,
            visible_songs=visible_songs_by_users[user_id],
            listened_songs=songs_listened_by_users[user_id],
        ))

    print "\n\tNumber of users in all train triplets: ", len(users_to_songs.keys())
    print "\tNumber of users in evaluation set: ", len(visible_songs_by_users.keys())
    return training_users


@log_time_spent()
def songs_to_users(filename="basic_data/train_triplets.txt", ratio=1.0):
    songs_to_users_dict = dict()
    with open(os.path.join(get_data_path(), filename), "r") as input_file:
        for line in input_file:
            if random.random() < ratio:
                user_id, song_id, _ = line.split()
                if song_id in songs_to_users_dict:
                    songs_to_users_dict[song_id].add(user_id)
                else:
                    songs_to_users_dict[song_id] = set([user_id])
    return songs_to_users_dict


@log_time_spent()
def songs_to_play_count(filename="basic_data/train_triplets.txt"):
    songs_to_play_count_dict = dict()
    with open(os.path.join(get_data_path(), filename), "r") as input_file:
        for line in input_file:
            _, song_id, _ = line.split()
            if song_id not in songs_to_play_count_dict:
                songs_to_play_count_dict[song_id] = 0
            else:
                songs_to_play_count_dict[song_id] += 1

    return songs_to_play_count_dict


@log_time_spent()
def users_to_songs(filename="basic_data/train_triplets.txt"):
    users_to_songs_dict = dict()
    with open(os.path.join(get_data_path(), filename), "r") as input_file:
        for line in input_file:
            user_id, song_id, _ = line.split()
            if user_id in users_to_songs_dict:
                users_to_songs_dict[user_id].add(song_id)
            else:
                users_to_songs_dict[user_id] = set([song_id])
    return users_to_songs_dict


# TODO: remove this
def songs_by_user(filename="basic_data/train_triplets.txt"):
    return users_to_songs(filename=filename)


@log_time_spent()
def songs_to_artists():
    # TODO: remove defaultdict
    artists_by_song = collections.defaultdict(list)
    h5 = hdf5_getters.open_h5_file_read(
        os.path.join(get_data_path(), "basic_data/msd_summary_file.h5")
    )

    for song in h5.root.metadata.songs:
        song_id = song["song_id"]
        artist_id = song["artist_id"]
        artists_by_song[song_id].append(artist_id)

    # close our file
    h5.close()
    return artists_by_song


# method used to traverse a dictionary instead of the whole training file directly
def play_count_by_song(visible_users_song_list):
    '''
    Popularity is computed only in the visible users, not in the full training data
    '''
    play_counts_by_song = collections.defaultdict(int)
    for song_list in visible_users_song_list.values():
        for song_id in song_list:
            play_counts_by_song[song_id] += 1
    return play_counts_by_song


@log_time_spent()
def artists_listened_by_users(visible_users_song_list, artists_list_by_song):
    listened_artists = collections.defaultdict(list)
    for user, song_list in visible_users_song_list.items():
        for song in song_list:
            artist_list = artists_list_by_song.get(song, [])
            listened_artists[user].extend(artist_list)
    return listened_artists


@log_time_spent()
def get_song_ranking_by_popularity(count_by_song):
    # Sort by play count
    return sorted(count_by_song.keys(), key=lambda s:count_by_song[s], reverse=True)


def get_popularity_recommendation(visible_songs_list, tau=500):
    count_by_song = play_count_by_song(visible_songs_list)
    ranked_songs = get_song_ranking_by_popularity(count_by_song)

    predicted_songs = []

    evaluation_users = visible_songs_list.keys()
    for index, user in enumerate(evaluation_users):
        predicted_songs.append([])
        for song in ranked_songs:
            if len(predicted_songs[index]) > tau:
                break
            if song not in visible_songs_list[user]:
                predicted_songs[index].append(song)
    return predicted_songs

@log_time_spent()
def get_popular_songs_with_artist_similarity_recommendation(visible_songs_list, tau=500):
    count_by_song = play_count_by_song(visible_songs_list)
    ranked_songs = get_song_ranking_by_popularity(count_by_song)
    predicted_songs = []
    artists_list_by_song = songs_to_artists()

    artists_by_user = artists_listened_by_users(visible_songs_list, artists_list_by_song)

    evaluation_users = visible_songs_list.keys()
    for index, user in enumerate(evaluation_users):
        predicted_songs.append([])
        for song in ranked_songs:
            # Do not include songs already listened by this user
            if song not in visible_songs_list[user]:
                predicted_songs[index].append(song)

            if len(predicted_songs[index]) > tau:
                break

        # Songs predicted for users here are ordered by popularity
        # Reorder songs by artists listened by the user
        current_position = 0
        for count, song in enumerate(predicted_songs[index]):
            song_artists = artists_list_by_song.get(song, [])
            for artist in song_artists:
                if artist in artists_by_user[user]:
                    predicted_songs[index].insert(current_position, predicted_songs[index].pop(count))
                    current_position += 1
                    break # go to next song

        if random.random() < 0.0005:
            print "Current index:", index
            print "number of songs listened by user {}:".format(user), len(visible_songs_list[user])
            # print "number of swapped songs: ", current_position
            print "Number of recommended songs for user:", len(predicted_songs[index])
            print "Play counts for recommended songs: ", [count_by_song[song] for song in predicted_songs[index][:20]]
            print "Songs in user artists:", []

    return predicted_songs


# TODO: move to `recommendations.py`
@log_time_spent()
def popularity_baseline(filename="basic_data/train_triplets.txt", ratio=0.09):
    visible_songs_by_users, songs_listened_by_users = generate_evaluation_data(filename, ratio=ratio)

    predicted_songs = get_popularity_recommendation(visible_songs_by_users, tau=500)

    listened_songs = [song_list for song_list in songs_listened_by_users.values()]

    mpak = metrics.mAPk(listened_songs, predicted_songs, k=1000)
    print "\n\t- Mean Average Precision (MAP @ tau={}): ".format(500), mpak

    plot_all_mpaks_by_different_taus(predicted_songs, listened_songs, title="popularity_baseline")

# TODO: move to `recommendations.py`
@log_time_spent()
def same_artist_baseline(filename="basic_data/train_triplets.txt", ratio=0.09):
    visible_songs_by_users, songs_listened_by_users = generate_evaluation_data(filename, ratio=ratio)
    predicted_songs = get_popular_songs_with_artist_similarity_recommendation(visible_songs_by_users, tau=500)
    listened_songs = [song_list for song_list in songs_listened_by_users.values()]
    mpak = metrics.mAPk(listened_songs, predicted_songs, k=500)
    print "\n\t- Mean Average Precision for Same Artist Baseline (MAP @ tau={}):".format(500), mpak
    plot_all_mpaks_by_different_taus(predicted_songs, listened_songs, title="same_artist_baseline_mapk")





if __name__ == "__main__":
    popularity_baseline(ratio=0.01)
