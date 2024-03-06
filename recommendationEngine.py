import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from data_loader import nlp, movies, similarity, movie_vectors, movie_history, save_to_movie_history
from botConfig import USER_QUERY_STOP_WORDS
import random


# recommendation functions
def get_recommendations_from_movie(id, num_recommend=10):
    if id not in movies.index:
        raise ValueError("Invalid uid")
    idx = movies.index.get_loc(id)
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    top_similar = sim_scores[1 : num_recommend + 1]
    movie_indices = [i[0] for i in top_similar]
    return movies.iloc[movie_indices]


def get_recommendations_from_query(user_query, num_recommend=10) -> tuple[pd.DataFrame, str]:
    # TODO test which components can be disabled
    nlp.Defaults.stop_words |= set(USER_QUERY_STOP_WORDS)
    query_doc = nlp(user_query, disable=["parser", "tagger", "lemmatizer"])
    nlp.Defaults.stop_words -= set(USER_QUERY_STOP_WORDS)
    query_vector = pd.DataFrame(query_doc.vector.reshape((1, -1)))

    search_query = " ".join([token.text for token in query_doc if not token.is_stop])
    if search_query == "":
        return pd.DataFrame(), search_query

    similarity = linear_kernel(query_vector, movie_vectors)
    if similarity[0].sum() == 0:
        return pd.DataFrame(), search_query
    sim_scores = list(enumerate(similarity[0]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    top_similar = sim_scores[1 : num_recommend + 1]
    indices = [i[0] for i in top_similar]

    return movies.iloc[indices], search_query


# bot functions
def random_movie() -> str:
    recommendations = movies.sample(5)
    response = "Here are some random movies: <br>"
    response += recommendations.to_html()
    return response


def search_movie(user_query: str) -> str:
    recommendations, search_query = get_recommendations_from_query(user_query)
    if search_query == "":
        response = "I couldn't find any keywords based on your input."
        response += recommend_movie()
    elif recommendations.empty:
        response = f"I couldn't find any keywords based on '{search_query}'"
        response += recommend_movie()
    else:
        response = f"Here are recommendations based on keywords '{search_query}': <br>"
        response += recommendations.to_html()
    return response


# TODO more testing
def recommend_movie() -> str:
    user_movie_history = [movie for movie in movie_history if movie[0] == 0]
    random_movies = random.sample(user_movie_history.index.tolist(), 5)
    for movie in random_movies:
        movie_id = movie[1]
        recommendations += get_recommendations_from_movie(movie_id, num_recommend=2)
    response = "Here are some movies that I think you'll like: <br>"
    response += recommendations.to_html()
    return response


def movie_menu(movie_id: int) -> str:
    try:
        recommendations = get_recommendations_from_movie(movie_id)
    except ValueError:
        response = f"I couldn't find any movie with the ID {str(movie_id)}."
    else:
        save_to_movie_history(movie_id)
        response = f"Here are some recommendations based on the movie {str(movie_id)}: <br>"
        response += recommendations.to_html()
    return response
