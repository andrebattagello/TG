import collections
import datetime
import functools
import os
import numpy as np
import random
import pylab
import utils.metrics as metrics
import utils.hdf5_getters as hdf5_getters

def log_time_spent(log_message="Time spent"):
    def decorator_provider(decorated):
        @functools.wraps(decorated)
        def decorator(*args, **kwargs):
            start_time = datetime.datetime.now()
            print "\n\t[Starting {}]".format(decorated.__name__)
            return_value = decorated(*args, **kwargs)
            end_time = datetime.datetime.now()
            print "\n\t[Time spent in {}]:".format(decorated.__name__), (end_time - start_time).seconds, "seconds"
            return return_value
        return decorator
    return decorator_provider

def get_data_path():
    data_path = os.path.realpath("../data")
    return data_path

@log_time_spent(log_message="songs to users")
def songs_to_users(filename="basic_data/train_triplets.txt", ratio=1.0):
    songs_to_users_dict = dict()
    with open(os.path.join(get_data_path(), filename), "r") as input_file:
        for line in input_file:
            if random.random()<ratio:
                user_id, song_id, _ = line.split()
                if song_id in songs_to_users_dict:
                    songs_to_users_dict[song_id].add(user_id)
                else:
                    songs_to_users_dict[song_id] = set([user_id])
    return songs_to_users_dict

@log_time_spent(log_message="songs to play count")
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


@log_time_spent(log_message="Users to songs")
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

def songs_by_user(filename="basic_data/train_triplets.txt"):
    return users_to_songs(filename=filename)

@log_time_spent(log_message="Songs to artists")
def songs_to_artists():
    # TODO: remove defaultdict
    artists_by_song = collections.defaultdict(list)
    h5 = hdf5_getters.open_h5_file_read(os.path.join(get_data_path(), "basic_data/msd_summary_file.h5"))

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


@log_time_spent(log_message="Artists listened by users")
def artists_listened_by_users(visible_users_song_list, artists_list_by_song):
    listened_artists = collections.defaultdict(list)
    for user, song_list in visible_users_song_list.items():
        for song in song_list:
            artist_list = artists_list_by_song.get(song, [])
            listened_artists[user].extend(artist_list)
    return listened_artists


# @log_time_spent(log_message="Songs to play counts")
# def songs_to_play_counts(filename="basic_data/train_triplets.txt"):
#     songs_to_play_counts = collections.defaultdict(int)
#     for line in open(os.path.join(get_data_path(), filename)):
#         user_id, song_id, play_count = line.split()
#         songs_to_play_counts[song_id] += 1
#     return songs_to_play_counts


@log_time_spent(log_message="Song ranking by popularity")
def get_song_ranking_by_popularity(count_by_song):
    # Sort by play count
    return sorted(count_by_song.keys(), key=lambda s:count_by_song[s], reverse=True)


@log_time_spent(log_message="Generating evaluation data")
def generate_evaluation_data(users_to_songs, ratio=0.09):
    visible_songs_by_users = dict()
    songs_listened_by_users = dict()

    user_ids = users_to_songs.keys()
    for user_id in user_ids:
        if random.random() > ratio:
            continue
        user_songs = list(users_to_songs[user_id])
        songs_len = len(user_songs)
        if songs_len < 2: # users that won't have listened history
            print "[no music] User id: {}".format(user_id)
        random.shuffle(user_songs)
        # first half stays in the evaluation
        visible_songs_by_users[user_id] = set(user_songs[:(songs_len/2)])
        # second half goes to the really listened songs
        songs_listened_by_users[user_id] = set(user_songs[(songs_len/2):])

    print "\n\tNumber of users in all train triplets: ", len(users_to_songs.keys())
    print "\n\tNumber of users in evaluation set: ", len(visible_songs_by_users.keys())

    return visible_songs_by_users, songs_listened_by_users

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

@log_time_spent(log_message="Artist similarity recommendation")
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

        # artists_by_user_set = set(artists_by_user[user])
        # predicted_songs[index] = sorted(predicted_songs[index],
        #                                 key= lambda song: (
        #                                          len(artists_by_user_set.intersection( set( artists_list_by_song.get(song, []) ) ) ) > 0,
        #                                          predicted_songs[index].index(song)
        #                                      )
        #                                 )

        if random.random() < 0.0005:
            print "Current index:", index
            print "number of songs listened by user {}:".format(user), len(visible_songs_list[user])
            # print "number of swapped songs: ", current_position
            print "Number of recommended songs for user:", len(predicted_songs[index])
            print "Play counts for recommended songs: ", [count_by_song[song] for song in predicted_songs[index][:20]]
            print "Songs in user artists:", []

    return predicted_songs


@log_time_spent(log_message="Popularity baseline")
def popularity_baseline(filename="basic_data/train_triplets.txt", ratio=0.09):
    visible_songs_by_users, songs_listened_by_users = generate_evaluation_data(filename, ratio=ratio)

    predicted_songs = get_popularity_recommendation(visible_songs_by_users, tau=500)

    listened_songs = [song_list for song_list in songs_listened_by_users.values()]

    mpak = metrics.mAPk(listened_songs, predicted_songs, k=1000)
    print "\n\t- Mean Average Precision (MAP @ tau={}): ".format(500), mpak

    plot_all_mpaks_by_different_taus(predicted_songs, listened_songs, title="popularity_baseline")

@log_time_spent(log_message="Same artist baseline")
def same_artist_baseline(filename="basic_data/train_triplets.txt", ratio=0.09):
    visible_songs_by_users, songs_listened_by_users = generate_evaluation_data(filename, ratio=ratio)
    predicted_songs = get_popular_songs_with_artist_similarity_recommendation(visible_songs_by_users, tau=500)
    listened_songs = [song_list for song_list in songs_listened_by_users.values()]
    mpak = metrics.mAPk(listened_songs, predicted_songs, k=500)
    print "\n\t- Mean Average Precision for Same Artist Baseline (MAP @ tau={}):".format(500), mpak
    plot_all_mpaks_by_different_taus(predicted_songs, listened_songs, title="same_artist_baseline_mapk")


def plot_all_mpaks_by_different_taus(predicted_songs, listened_songs, title="all_mapks"):
    all_taus = range(5,55)
    all_mpaks = []
    for tau in all_taus:
        all_mpaks.append(metrics.mAPk(listened_songs, predicted_songs, k=tau))

    pylab.title("mAPk for different Taus")
    pylab.xlabel("Tau (k)")
    pylab.ylabel("mAPk")
    pylab.xlim(0, 505)
    pylab.plot(all_taus, all_mpaks)
    pylab.savefig("results/{}-{}.png".format(title, datetime.datetime.now().strftime("%d-%m-%H-%M-%S")))


def convert_train_triplets_to_indexes():
    user_index = 0
    song_index = 0
    user_to_index = {}
    song_to_index = {}
    train_triplets_filename = "basic_data/train_triplets.txt"
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



if __name__ == "__main__":
    popularity_baseline(ratio=0.01)
