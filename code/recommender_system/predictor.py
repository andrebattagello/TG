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

    # TODO: implement this!
    def _pre_compute_all_scores(self, listened_items):
        pass

    @utils.log_time_spent(log_message="Score items")
    def score_items(self, user_items, all_items):
        songs_score = {}
        for song in all_items:
            songs_score[song] = 0.0
            for user_song in user_items:
                weight = 0.0
                # calculating weight
                first_user_set_len = len(self.songs_to_users[song])
                second_user_set_len = len(self.songs_to_users[user_song])
                intersection_set_size = float(len(self.songs_to_users[song] & self.songs_to_users[user_song]))
                if intersection_set_size > 0:
                    denominator = (first_user_set_len ** -self.alfa *
                                   second_user_set_len ** -(1.0-self.alfa))
                    weight = intersection_set_size * denominator
                # finished calculating weight
                songs_score[song] += weight ** self.q
        return songs_score

