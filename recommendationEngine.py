import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
import re
from spacy_loader import nlp


DATASET_PATH = "data/ml-latest-small/"
USER_QUERY_STOP_WORDS = {
    "movie",
    "recommend",
    "look",
    "find",
    "want",
    "good",
    "like",
    "watch",
    "see",
    "search",
}

# TODO where should i even put this code
# initialize
print("Loading movie dataset...")
movies = pd.read_csv(DATASET_PATH + "movies.csv", index_col="movieId")
df_tags = pd.read_csv(DATASET_PATH + "tags.csv")
movies["tags"] = (
    df_tags.groupby("movieId")["tag"]
    .apply(lambda x: " ".join(x))
    .reset_index()["tag"]
    .fillna("")
)  # join with the tags table
movies["tags"] = movies["tags"].fillna("")  # Replace null data with empty string
movies["combined_info"] = movies["title"] + movies["genres"] + movies["tags"]


# analyze
print("Analyzing movie dataset with spaCy...")
movie_pipe = nlp.pipe(movies["combined_info"], disable=["parser", "tagger", "lemmatizer"], n_process=-1)
# TODO test which components can be disabled
movie_doc = list(movie_pipe)
movie_vectors = pd.DataFrame([doc.vector for doc in movie_doc])
similarity = linear_kernel(movie_vectors, movie_vectors)


# TODO dump processed data and reuse


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
    # analyze query to extact keywords
    user_query_doc = nlp(user_query)
    search_query = [token.lemma_ for token in user_query_doc if not token.is_stop and not token.is_punct and token.lemma_ not in USER_QUERY_STOP_WORDS]
    search_query = " ".join(search_query).strip()

    if search_query == "":
        return pd.DataFrame(), search_query

    # TODO test which components can be disabled
    query_vector = nlp(search_query).vector
    query_vector = pd.DataFrame(query_vector.reshape((1, -1)))
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
    elif recommendations.empty:
        response = f"I couldn't find any recommendations based on '{search_query}'"
    else:
        response = f"Here are recommendations based on keywords '{search_query}': <br>"
        response += recommendations.to_html()
    return response

# TODO
def recommend_movie() -> str:
    recommendations = movies.sample(5)
    response = "Here are some random movies: <br>"
    response += recommendations.to_html()
    return response

def movie_menu(movie_id: int) -> str:
    recommendations = get_recommendations_from_movie(movie_doc)
    response = f"Here are some recommendations based on the movie {str(movie_id)}: <br>"
    response += recommendations.to_html()
    return response
