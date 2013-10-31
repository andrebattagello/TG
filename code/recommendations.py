import datetime
import json
import os
import data_utils.data_utils as data_utils

import utils.metrics as metrics

from recommender_system import recommender
from recommender_system import predictor

# TODO: move to another place ?
def _sorted_dict(d):
    return sorted(d.keys(),
                  key=lambda s: d[s],
                  reverse=True)


def song_similarity_recommendation(num_of_processes=3,
                                   num_of_users=1000,
                                   q=3.0,
                                   alfa=0.1):
    training_data_filename = "basic_data/train_triplets.txt"

    test_users = data_utils.load_test_users(test_users_index=1)
    print "\tGenerated test users"
    print "\nNumber of users in test set: {}".format(len(test_users))
    print "\tRecommending to {} users".format(num_of_users)

    user_ids = [user_data["user_id"] for user_data in test_users[:num_of_users]]
    visible_user_to_songs = {}
    listened_user_to_songs = {}
    for user_data in test_users:
        visible_user_to_songs[user_data["user_id"]] = user_data["visible_songs"]
        listened_user_to_songs[user_data["user_id"]] = user_data["listened_songs"]
    print "\tLoaded test users data correctly"

    songs_to_users = data_utils.songs_to_users(filename=training_data_filename)
    print "\n\t- Generated songs_to_users"

    songs_to_play_count = data_utils.songs_to_play_count(filename=training_data_filename)
    print "\n\tGenerated songs to play count"

    sorted_songs_by_play_count = _sorted_dict(songs_to_play_count)
    stochastic_recommender = recommender.StochasticRecommender(all_items=sorted_songs_by_play_count)
    print "\n\tRecommender initialized"

    stochastic_recommender.NUM_OF_PROCESSES = num_of_processes

    del songs_to_play_count
    print "\n\tDeleting songs_to_play_count"
    del sorted_songs_by_play_count
    print "\n\tDeleted sorted_songs_by_play_count"

    song_similarity_predictor = predictor.SongSimilatiryPredictor(songs_to_users=songs_to_users)
    print "\n\tPredictor initialized ok"
    stochastic_recommender.add_predictor(song_similarity_predictor)
    stochastic_recommender.add_predictors_weight([1.0])
    print "\n\tPredictor setup ok"

    recommendations = stochastic_recommender.recommend_to_users(
        user_ids,
        visible_user_to_songs
    )

    print "\n\tFinished generating recommendations"
    listened_songs = [listened_user_to_songs[user_id] for user_id in user_ids]
    print "\n\t--- Number of recommendations:", len(recommendations)
    # mapk = metrics.mAPk(listened_songs, recommendations)
    # print "\n\t*** Mean Average Precision", mapk

    results = {
        "number_of_users": len(recommendations),
        "user_ids": user_ids,
        "recommendations": recommendations,
        "listened_songs": [list(song_set) for song_set in listened_songs],
        # "mapk": mapk
    }

    additional_tag = "q={},alfa={}".format(str(q), str(alfa))
    # Save results to an external file
    results_filename = "results/song_similarity_recommendation_results_{}-{}.json".format(
        datetime.datetime.now().strftime("%d-%m-%H-%M-%S"),
        additional_tag,
    )
    # TODO: use "save_json method"
    with open(os.path.join(data_utils.get_data_path(), results_filename), "w") as json_results_file:
        json.dump(results, json_results_file)

    print "finito"


if __name__ == '__main__':
    song_similarity_recommendation(read_json_data=False,
                                   write_json_file=False,
                                   num_of_processes=10)
