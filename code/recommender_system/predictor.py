import datetime

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
    alfa = 0.1

    q_distribution = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]

    def __init__(self, songs_to_users, alfa=0.1):
        super(SongSimilatiryPredictor, self).__init__()
        self.songs_to_users = songs_to_users
        self.alfa = alfa

    def _pre_compute_all_scores(self, listened_items, all_items):
        pass

    def score_items(self, user_items, all_items):
        start_time = datetime.datetime.now()
        songs_score = {}
        for q in self.q_distribution:
            songs_score[q] = {}
        for song in all_items:
            for q in self.q_distribution:
                songs_score[q][song] = 0.0
            for user_song in user_items:
                weight = 0.0
                # calculating weight
                first_user_set_len = len(self.songs_to_users[song])
                second_user_set_len = len(self.songs_to_users[user_song])
                intersection_set_size = float(len(self.songs_to_users[song] & self.songs_to_users[user_song]))
                if intersection_set_size > 0:
                    denominator = (first_user_set_len ** -self.alfa *
                                   second_user_set_len ** -(1.0-self.alfa))
                    # TODO: weight is an array, that computes the results for different alfas
                    weight = intersection_set_size * denominator
                # finished calculating weight
                for q in self.q_distribution:
                    songs_score[q][song] += weight ** q
        end_time = datetime.datetime.now()
        print "[score items] Finished score_items - Took {} seconds".format((end_time-start_time).seconds)
        return songs_score


