import collections
import cloud
import datetime
import functools
import os
import random
import utils.metrics as metrics
import utils.hdf5_getters as hdf5_getters

# def songs_to_tracks():
#     print "Starting songs to tracks"
#     songs_to_tracks = collections.defaultdict(list)
#     for line in open(os.path.join(get_data_path(), "basic_data/taste_profile_song_to_tracks.txt")):
#         line_contents = line.split()
#         song_id = line_contents[0]
#         # ignore songs without track information
#         if len(line_contents[1:]):
#             songs_to_tracks[song_id].extend(line_contents[1:])
#     print "Songs to tracks OK"
#     print "Number of songs in songs to tracks: ", len(songs_to_tracks.keys())
#     return songs_to_tracks


def log_time_spent(log_message="Time spent"):
    def decorator_provider(decorated):
        @functools.wraps(decorated)
        def decorator(*args, **kwargs):
            start_time = datetime.datetime.now()
            return_value = decorated(*args, **kwargs)
            end_time = datetime.datetime.now()
            print "[{}]:".format(log_message), (end_time - start_time).seconds, "seconds"
            return return_value

        return decorator
    return decorator_provider

def get_data_path():
    if cloud.running_on_cloud():
        data_path = "/data/million_song_data/"
    else:
        data_path = "/Users/andrebattagello/Projects/TG/million_song/data/"
    return data_path

def songs_by_user(filename="basic_data/train_triplets.txt"):
    songs_by_user = collections.defaultdict(list)
    for line in open(os.path.join(get_data_path(), filename)):
        user_id, song_id, play_count = line.split()
        songs_by_user[user_id].append(song_id)
    return songs_by_user

@log_time_spent(log_message="Songs to artists")
def songs_to_artists():
    songs_to_artists = collections.defaultdict(list)
    h5 = hdf5_getters.open_h5_file_read(os.path.join(get_data_path(), "basic_data/msd_summary_file.h5"))
    for song in h5.root.metadata.songs:
        song_id = song["song_id"]
        artist_id = song["artist_id"]
        songs_to_artists[song_id].append(artist_id)
    return songs_to_artists


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


@log_time_spent(log_message="Songs to play counts")
def songs_to_play_counts(filename="basic_data/train_triplets.txt"):
    songs_to_play_counts = collections.defaultdict(int)
    for line in open(os.path.join(get_data_path(), filename)):
        user_id, song_id, play_count = line.split()
        songs_to_play_counts[song_id] += 1
    return songs_to_play_counts



@log_time_spent(log_message="Song ranking by popularity")
def get_song_ranking_by_popularity(count_by_song):
    # Sort by play count
    return sorted(count_by_song.keys(), key=lambda s:count_by_song[s], reverse=True)

# TODO: stats over all the training data
# def calculate_max_song_list_size():
#     return max(map(lambda song_list: len(song_list), songs_by_user().values()))

def general_stats():
    # Number of users
    # Number of songs
    # Number of artists
    # Years of songs - plot songs by year
    # Clusterization on tempo/other features of songs
    # Average songs by user
    # Average users by song
    # Percent of users with less than X songs -> long tail
    # Percent of songs listened by more than X users - long tail
    # % of users songs in N thousand top popular music
    pass

@log_time_spent(log_message="Generating evaluation data")
def generate_evaluation_data(filename, ratio=0.0):
    visible_songs_by_users = dict()
    songs_listened_by_users = dict()

    song_list_by_user = songs_by_user(filename)
    user_ids = song_list_by_user.keys()
    for user_id in user_ids:
        if random.random() > ratio:
            continue
        user_songs = song_list_by_user[user_id]
        songs_len = len(user_songs)
        random.shuffle(user_songs)
        # first half stays in the evaluation
        visible_songs_by_users[user_id] = user_songs[:(songs_len/2)]
        # second half goes to the really listened songs
        songs_listened_by_users[user_id] = user_songs[(songs_len/2):]

    print "\n\t- Number of users in all train triplets: ", len(song_list_by_user.keys())
    print "\n\t- Number of users in evaluation set: ", len(visible_songs_by_users.keys())

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
            if len(predicted_songs[index]) > tau:
                break
            # Remove songs already listened by this user
            if song not in visible_songs_list[user]:
                predicted_songs[index].append(song)

        # songs predicted for users here are ordered by popularity

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
            print "number of swapped songs: ", current_position
            print "Play counts: ", [count_by_song[song] for song in predicted_songs[index][:20]]
            print "Songs in user artists:", []

    return predicted_songs


@log_time_spent(log_message="Popularity baseline")
def popularity_baseline(filename="basic_data/train_triplets.txt", ratio=0.09):
    visible_songs_by_users, songs_listened_by_users = generate_evaluation_data(filename, ratio=ratio)
    predicted_songs = get_popularity_recommendation(visible_songs_by_users, tau=500)
    listened_songs = [song_list for song_list in songs_listened_by_users.values()]
    mpak = metrics.mAPk(listened_songs, predicted_songs, k=1000)
    print "\n\t- Mean Average Precision (MAP @ tau={}): ".format(500), mpak

@log_time_spent(log_message="Same artist baseline")
def same_artist_baseline(filename="basic_data/train_triplets.txt", ratio=0.09):
    # TODO: memory profiling
    visible_songs_by_users, songs_listened_by_users = generate_evaluation_data(filename, ratio=ratio)
    predicted_songs = get_popular_songs_with_artist_similarity_recommendation(visible_songs_by_users, tau=500)
    listened_songs = [song_list for song_list in songs_listened_by_users.values()]
    mpak = metrics.mAPk(listened_songs, predicted_songs, k=500)
    print "\n\t- Mean Average Precision for Same Artist Baseline (MAP @ tau={}):".format(500), mpak

if __name__ == "__main__":
    popularity_baseline(ratio=0.01)
    # jid = cloud.call(set_user_data, _vol="dataset-volume")
    # songs_by_user, play_counts_by_song = cloud.result(jid)
    # print "Songs by users size: ", len(songs_by_user)
