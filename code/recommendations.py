import datetime
import json
import os
import main
import pprint

import utils.metrics as metrics

from recommender_system import recommender
from recommender_system import predictor

# user_min = 0
# user_max = 10
def _sorted_dict(d):
    return sorted(d.keys(),
                  key=lambda s: d[s],
                  reverse=True)

def generate_songs_to_users_json(songs_to_users, filename="results/songs_to_users.json"):
    with open(os.path.join(main.get_data_path(), filename), "w") as json_dump_file:
        print "\n\tGenerating songs to users dump file"
        json_dict = {song_id: list(song_set) for song_id, song_set in songs_to_users.items()}
        json.dump(json_dict, json_dump_file)


def song_similarity_recommendation(read_json_data=False,
                                   write_json_file=False,
                                   num_of_processes=4,
                                   recommended_users_ratio=0.0001):
    training_data_filename = "basic_data/train_triplets.txt"

    # TODO: json.dumps pre computed
    users_to_songs = main.users_to_songs(filename=training_data_filename)
    print "\n\t- Generated users_to_songs"

    users_to_songs_visible, users_to_songs_complete = main.generate_evaluation_data(
        users_to_songs,
        ratio=recommended_users_ratio # 0.0001 ~= 100 users
    )

    print "\n\t- Generated evaluation data"
    del users_to_songs
    print "\n\t- Deleted users_to_songs"

    print "\n\t- Going to generate songs_to_users"
    songs_to_users = {}

    if read_json_data and not write_json_file:
        print "\n\t Reading data from JSON file"
        with open(os.path.join(main.get_data_path(), "results/songs_to_users.json"), "r") as json_dump_file:
            songs_to_users_data = json.load(json_dump_file)
            songs_to_users = {song_id: set(song_list) for song_id, song_list in songs_to_users_data.items()}
    else:
        songs_to_users = main.songs_to_users(filename=training_data_filename)

    print "\n\t- Generated songs_to_users"

    if write_json_file:
        generate_songs_to_users_json(songs_to_users)

    songs_to_play_count = main.songs_to_play_count(filename=training_data_filename)
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
        users_to_songs_visible.keys(),
        users_to_songs_visible
    )
    print "\n\tFinished generating recommendations"
    listened_songs = [song_set for song_set in users_to_songs_complete.values()]
    mapk = metrics.mAPk(listened_songs, recommendations)
    print "Mean Average Precision", mapk
    print "Number of recommendations:", len(recommendations)

    results = {
        "number_of_users": len(recommendations),
        "recommendations": recommendations,
        "listened_songs": [list(song_set) for song_set in listened_songs],
        "mapk": mapk,
    }

    # Save results to an external file
    results_filename = "results/song_similarity_recommendation_results_{}.json".format(
        datetime.datetime.now().strftime("%d-%m-%H-%M-%S")
    )
    with open(os.path.join(main.get_data_path(), results_filename), "w") as json_results_file:
        json.dump(results, json_results_file)

    print "finito"


if __name__ == '__main__':
    song_similarity_recommendation()
