import datetime
import utils.utils as utils
import random

import multiprocessing
import Queue

class Recommender(object):
    """
    Defines a generic Recommender interface
    """
    all_items = []
    predictors = []
    predictors_weight = []
    # parameter used in metrics calculation - how to separate the metrics usage from the
    # recommender implementation ?
    tau = 500

    def __init__(self, all_items=None):
        self.all_items = all_items if all_items else []

    def add_predictor(self, predictor):
        self.predictors.append(predictor)

    def add_predictors_weight(self, predictors_weight):
        self.predictors_weight = predictors_weight if predictors_weight else []

    def _recommend_to_user(self, user_id, user_to_items_visible):
        """
        Return the list of recommended items for a given user with `user_id`
        Parameters:
            - user_id: user identifier
            - user_to_items_visible: a dict with
        """
        return []

    def recommend_to_users(self, all_users, user_to_items_visible):
        """
        Recommend songs given a list of users and the mapping from user to items
        Params:
            - all_users: list of `user_ids`
            - user_to_items_visible: dict with list of items for each user given his `user_id`
        Return a list of lists, where each list represents the recommended songs for
        the users, considering the order of the users
        """
        return []


class StochasticRecommender(Recommender):
    NUM_OF_PROCESSES = 10
    MAX_USERS_TO_RECOMMEND = 100

    def __init__(self, all_items=None):
        super(StochasticRecommender, self).__init__(all_items=all_items)


    def _filter_recommended_songs(self, user_id, recommended_songs, user_to_items_visible):
        filtered_songs = []
        recommended_count = 0

        for song in recommended_songs:
            if recommended_count >= self.tau:
                break
            if song not in user_to_items_visible[user_id]:
                filtered_songs.append(song)
                recommended_count += 1

        return filtered_songs

    def _get_stochastic_index(self):
        value = random.random()
        for predictor_index, probability in enumerate(self.predictors_weight):
            if value < probability:
                return predictor_index
            value -= probability
        # should not return by here
        return 0

    def stochastic_recommendation(self, all_recommendations):
        current_indexes = [0] * len(self.predictors)
        recommended_songs = []
        recommended_count = 0
        print "\n\t--- Combining recommendations"
        while (recommended_count < self.tau):
            predictor_index = self._get_stochastic_index()
            next_song_index = current_indexes[predictor_index]
            chosen_recommendation = all_recommendations[predictor_index]

            chosen_song = chosen_recommendation[next_song_index]
            if chosen_song not in recommended_songs:
                recommended_songs.append(chosen_song)
                recommended_count += 1
            current_indexes[predictor_index] += 1

        return recommended_songs

    def _recommend_to_user(self, user_id, user_to_items_visible):
        predictors_recommendations = []
        for predictor in self.predictors:
            print "\n\tStarting predictor {}".format(predictor._id)
            sorted_songs = []
            if user_id in user_to_items_visible:
                print "\n\t--- Scoring items for user_id {}".format(user_id)
                songs_score = predictor.score_items(user_to_items_visible[user_id],
                                                    self.all_items)
                print "\n\t=== Scored items for user_id {}".format(user_id)
                sorted_songs = sorted(songs_score.keys(),
                                      key=lambda s: songs_score[s],
                                      reverse=True)
            else:
                sorted_songs = self.all_items

            valid_songs_to_recommend = self._filter_recommended_songs(user_id,
                                                                      sorted_songs,
                                                                      user_to_items_visible)
            predictors_recommendations.append(valid_songs_to_recommend)

        return self.stochastic_recommendation(predictors_recommendations)


    def recommend_to_users(self, users_to_recommend, user_to_items_visible):
        recommendations = []
        start_time = datetime.datetime.now()
        print "\n\t- Recommending to users"

        # dirty check to avoid errors
        if len(self.predictors) != len(self.predictors_weight):
            raise ValueError("Predictors and its distributions don't match")

        listened_songs = set()
        for user_id, song_set in users_to_recommend.items():
            for song in song_set:
                if song not in song_set:
                    listened_songs.add(song)

        print "\n\t- Listened songs setup ok"

        for predictor in self.predictors:
            predictor._pre_cache_scores(listened_songs, self.all_items)

        print "\n\t Cached scores for listened songs!"

        for user_id in users_to_recommend:
            user_recomendations = self._recommend_to_user(user_id, user_to_items_visible)
            recommendations.append(user_recomendations)

        end_time = datetime.datetime.now()
        print "[recommend_to_users] Finished Recommend to Users - Took {} seconds".format((end_time-start_time).seconds)

        # list of lists of recommendations for each user
        return recommendations
