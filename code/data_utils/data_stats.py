import collections
import datetime
import utils.metrics as metrics
import pylab
import sys

import main


def song_list_size_by_user():
    pass


def stats(plot_results=False):
    visible_songs_by_users, songs_listened_by_users = main.generate_evaluation_data(
        "basic_data/train_triplets.txt", ratio=1
    )
    play_count_by_song = main.play_count_by_song(visible_songs_by_users)
    artist_list_by_song = main.songs_to_artists()

    all_songs = []
    Song = collections.namedtuple("Song", ["id", "play_count", "artists"])
    for song_id, play_count in play_count_by_song.items():
        song = Song(id=song_id,
                    play_count=play_count,
                    artists=artist_list_by_song.get(song_id, None))
        all_songs.append(song)

    # print "Ordered by play_count:"
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(sorted(all_songs, key=lambda s: s.play_count, reverse=True)[:10])
    x = range(len(all_songs))
    play_counts = [s.play_count for s in sorted(all_songs, key=lambda s: s.play_count, reverse=True)]

    if plot_results:
        pylab.title("Songs by popularity")
        pylab.xlabel("Songs by popularity")
        pylab.ylabel("Play counts")
        pylab.xlim(0, 1000) # empirical :P
        pylab.plot(x, play_counts, color="blue")
        # pylab.scatter(x, play_counts)
        pylab.savefig("results/play_counts-{}.png".format(datetime.datetime.now().strftime("%d-%m-%H-%M-%S")))

    avg_play_count = sum(song.play_count for song in all_songs) / len(all_songs)
    print "Average play count by song"
    print avg_play_count

    more_than_avg_play_count = 0
    for song in all_songs:
        if song.play_count > avg_play_count:
            more_than_avg_play_count += 1

    print "Number of songs with more than avg play counts: ", more_than_avg_play_count
    print "Number of total songs: ", len(all_songs)


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


if __name__ == '__main__':
    print sys.argv
    # TODO: argparse
    stats()

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
