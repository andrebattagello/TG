"""
Recommender system implementation based on F Aioli implementation, available at:
http://www.math.unipd.it/~aiolli/CODE/MSD/

We use here the same concept to design our Recommender System in 2 parts:
    1) the `Predictor`, responsible for scoring values to the all the items for each user
    2) the `Recommender`, responsible for combining the scores generated by different predictors and
       ranking the items, providing the final recommendations for all the users
"""


import datetime
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

    def _recommend_to_user_worker(self,
                                  users_queue,
                                  user_to_items_visible,
                                  recommendations_dict,
                                  process_id):
        print "\n\tStarting Process with ID={}".format(process_id)
        user_ids = []
        while True:
            try:
                user_index, user_id = users_queue.get(block=True, timeout=5)
            except Queue.Empty:
                print "\n\t- Finished Process ID={}, thread quitting".format(process_id)
                print "\n\t- Processed the following User IDs:", user_ids
                break

            predictors_recommendations = []
            for predictor in self.predictors:
                sorted_songs = {}
                print "\n\tStarting predictor {}".format(predictor._id)

                if user_id in user_to_items_visible:
                    print "\n\t--- Scoring items for user_id {}".format(user_id)
                    songs_score = predictor.score_items(user_to_items_visible[user_id],
                                                        self.all_items)
                    print "\n\t=== Scored items for user_id {}".format(user_id)

                    # TODO: generalize to the case where there's no distribution of parameters
                    # or consider that there's only 1 q even if there's no distribution :)
                    for q in predictor.q_distribution:
                        sorted_songs[q] = sorted(songs_score[q].keys(),
                                                 key=lambda s: songs_score[q][s],
                                                 reverse=True)
                else:
                    print "******************WAT, should't be here!!!**********************"
                    for q in predictor.q_distribution:
                        sorted_songs[q] = self.all_items

                predictor_recommendation = {}
                for q in predictor.q_distribution:
                    predictor_recommendation[q] = self._filter_recommended_songs(user_id,
                                                                                 sorted_songs[q],
                                                                                 user_to_items_visible)

                print "\n\tFinished predictor: index={}, user_id={} / process={}".format(user_index,
                                                                                         user_id,
                                                                                         process_id)
                predictors_recommendations[predictor._id] = predictor_recommendation

            recommendations_dict[user_id] = predictors_recommendations
            user_ids.append(user_id)
            print "\n\t- Finished user index={}, user_id={}".format(user_index, user_id)

    def recommend_to_users(self, users_to_recommend, user_to_items_visible):
        start_time = datetime.datetime.now()
        print "- Recommending to users"

        # dirty check to avoid errors
        if len(self.predictors) != len(self.predictors_weight):
            raise ValueError("Predictors and its distributions don't match")

        users_queue = multiprocessing.JoinableQueue()
        manager = multiprocessing.Manager()
        recommendations_dict = manager.dict()

        print "\n\t- Setting users_queue"
        for user_index, user_id in enumerate(users_to_recommend):
            users_queue.put((user_index, user_id))

        print "\n\t- Queue set ok, approximate number of users: ", users_queue.qsize()

        processes = []
        for process_id in xrange(self.NUM_OF_PROCESSES):
            p = multiprocessing.Process(
                target=self._recommend_to_user_worker,
                args=(users_queue, user_to_items_visible, recommendations_dict, process_id)
            )
            p.start()
            print "\n\t- Starting process P{}".format(process_id)
            processes.append(p)

        print "\n\t- Waiting processes to finish"
        for p in processes:
            p.join()

        print "\n\t- Processes finished"

        predictors_recommendations = [recommendations_dict[user_id] for user_id in users_to_recommend]
        print "Generated recommendations list"

        end_time = datetime.datetime.now()
        print "[recommend_to_users] Finished Recommend to Users - Took {} seconds".format((end_time-start_time).seconds)

        # list of lists of recommendations for each user
        return predictors_recommendations
