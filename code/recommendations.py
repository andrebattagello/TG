import main
import utils.metrics as metrics

from recommender_system import recommender
from recommender_system import predictor

# user_min = 0
# user_max = 10

def song_similarity_recommendation():

    # users are stored using ids
    songs_to_users, users_to_songs, songs_to_play_count = main.training_data(
        filename="basic_data/train_triplets.txt"
    )
    print "=============== generated training data"

    users_to_songs_visible, users_to_songs_complete = main.generate_evaluation_data(
        users_to_songs,
        ratio=0.09
    )
    print "=============== evaluation data ok"

    sorted_songs_by_play_count = sorted(songs_to_play_count.keys(),
                                        key=lambda s: songs_to_play_count[s],
                                        reverse=True)

    stochastic_recommender = recommender.StochasticRecommender(all_items=sorted_songs_by_play_count)
    print "=============== recommender ok"
    song_similarity_predictor = predictor.SongSimilatiryPredictor(songs_to_users=songs_to_users)
    print "=============== predictor ok"

    stochastic_recommender.add_predictor(song_similarity_predictor)
    stochastic_recommender.add_predictors_weight([1.0])
    print "=============== predictor setup ok"

    recommendations = stochastic_recommender.recommend_to_users(
        users_to_songs_visible.keys(),
        users_to_songs_visible
    )
    print "=============== recommendations ok"

    listened_songs = [song_set for song_set in users_to_songs_complete.values()]
    mapk = metrics.mAPk(listened_songs, recommendations)
    print "Mean Average Precision", mapk


if __name__ == '__main__':
    song_similarity_recommendation()
