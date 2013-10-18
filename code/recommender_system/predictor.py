import math
import collections

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

    q = 3.0 # locality ponderation : TODO: find a better name
    alfa = 0.13

    def __init__(self, songs_to_users):
        super(SongSimilatiryPredictor, self).__init__()
        self.songs_to_users = songs_to_users

    def _weight(self, song_1, song_2):
        first_user_set = self.songs_to_users[song_1]
        second_user_set = self.songs_to_users[song_2]
        user_intersection_set_size = float(len(first_user_set & second_user_set))
        if user_intersection_set_size > 0:
            denominator = (math.pow(len(first_user_set), self.alfa) *
                           math.pow(len(second_user_set), (1.0-self.alfa)))
            # print "------------ return some weight"
            return user_intersection_set_size/denominator
        return 0.0

    def score_items(self, user_items, all_items):
        songs_score = collections.defaultdict(float)
        print "====================== scoring items"
        for song in all_items:
            songs_score[song] = 0.0
            if song not in self.songs_to_users:
                continue # ie, no user listened to this song
            for user_song in user_items:
                # print "---------------- calculating weight"
                weight = self._weight(song, user_song)
                if user_song not in self.songs_to_users:
                    continue # not sure if this is necessary
                songs_score[song] += math.pow(weight, self.q)
        print "====================== finished scoring items"
        return songs_score


