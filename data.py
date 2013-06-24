import collections
import utils

Song = collections.namedtuple('Song', ['song_number', 'play_count'])

users = {}
songs = {}

songs_by_user = collections.defaultdict(list)
play_counts_by_song = collections.defaultdict(int)


def set_user_data():
    # Associate a number to each user
    # for n, line in enumerate(open("data/kaggle_users.txt"), start=1):
    #     user_id = line.strip()
    #     users[user_id] = n

    # # Associate a number to each song
    # for line in open("data/kaggle_songs.txt"):
    #     song_id, song_number = line.split()
    #     songs[song_id] = song_number

    # Create a list of the song list of each user
    for line in open("data/train_triplets.txt"):
    # for line in open("data/kaggle_visible_evaluation_triplets.txt"):
        user_id, song_id, play_count = line.split()
        # user_number = users[user_id]
        # song_number = songs[song_id]
        play_counts_by_song[song_id] += int(play_count)
        songs_by_user[user_id].append(song_id)

    print "Train Triplets read OK"
    # print "Number of users: ", len(users)
    # print "Number of songs: ", len(songs)


def calculate_max_song_list_size():
    max_size = 0
    for user_number, song_list in songs_by_user.items():
        song_list_size = len(song_list)
        max_size = max(song_list_size, max_size)

    print "Max list size: ", max_size


def get_song_ranking_by_popularity(threshold=None):
    song_list_with_play_count = []
    for song_number, play_count in play_counts_by_song.items():
        song_list_with_play_count.append(Song(song_number, int(play_count)))

    # Sort by play count
    song_list_with_play_count.sort(key=lambda song: -song.play_count)

    if not threshold or threshold > len(song_list_with_play_count):
        threshold = len(song_list_with_play_count)

    return [song.song_number for song in song_list_with_play_count][:threshold]


def get_mpak_by_popularity_ranking(k=1000):
    # song_count = len(songs)
    user_count = len(songs_by_user)
    songs_by_popularity = get_song_ranking_by_popularity(k)
    predicted_rankings = [songs_by_popularity]*user_count
    print "Predicted Ranking OK"
    actual_results = [song_list for user, song_list in songs_by_user.items()]
    print "Real Results OK"

    mean_average_precision = utils.mAPk(actual_results, predicted_rankings, k)
    print "mAP (k=1000): ", mean_average_precision

set_user_data()
