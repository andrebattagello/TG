import datetime
import math
import json

import collections
from utils import utils

class Predictor(object):
    """
    Implements a generic Predictor interface
    """

    songs_to_users = {}


    def __init__(self):
        pass

    def score_items(self, user_items, all_items):
        """
        Returns a dict with all the score for each song
        """
        return {}

    def _weight(self, song, user_song):
        """
        Return a float
        """
        return 0.0


class PopularityPredictor(Predictor):
    pass


class SongSimilatiryPredictor(Predictor):

    _id = "song_similarity"
    q = 3.0 # locality ponderation : TODO: find a better name
    alfa = 0.13
    scores_cache = {}

    def __init__(self, songs_to_users):
        super(SongSimilatiryPredictor, self).__init__()
        self.songs_to_users = songs_to_users

    def _pre_cache_scores(self, listened_items, all_items):
        print "\n\t[Pre cache] Starting..."
        start_time = datetime.datetime.now()
        count = 0
        for song in all_items:
            for other_song in listened_items:
                count += 1
                self._weight(song, other_song, cache_result=True)
                if count % 10000000 == 0:
                    current_time = datetime.datetime.now()
                    print "[Pre caching items] Current elapsed time: {} seconds".format(
                        (current_time-start_time).seconds
                    )
                    print "[Pre caching items] Current count in cache: ", count
                    print "[Pre caching items] Average: {} insertions/sec".format(
                        count/((current_time-start_time).seconds), ""
                    )
        end_time = datetime.datetime.now()
        print "[Pre caching items] Took {} seconds".format(
            (end_time-start_time).seconds
        )
        print "[Pre caching items] Total count: {}".format(count)

    def _weight(self, song, user_song, cache_result=False):
        weight = self.scores_cache.get(song + user_song)
        if not weight:
            weight = 0.0
            first_user_set_len = len(self.songs_to_users[song])
            second_user_set_len = len(self.songs_to_users[user_song])
            intersection_set_size = float(
                len(self.songs_to_users[song] & self.songs_to_users[user_song])
            )
            if intersection_set_size > 0:
                denominator = (
                    (first_user_set_len ** -self.alfa) * (second_user_set_len ** -(1.0-self.alfa))
                )
                weight = intersection_set_size * denominator
            if cache_result:
                self.scores_cache[song + user_song] = weight
        return weight

    def score_items(self, user_items, all_items):
        start_time = datetime.datetime.now()
        songs_score = {}
        for song in all_items:
            songs_score[song] = 0.0
            for user_song in user_items:
                weight = self._weight(song, user_song)
                songs_score[song] += weight ** self.q
        end_time = datetime.datetime.now()
        print "[score items] Finished score_items - Took {} seconds".format((end_time-start_time).seconds)
        return songs_score


