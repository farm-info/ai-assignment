import csv
import pandas as pd

import spacy
from sklearn.metrics.pairwise import linear_kernel
from botConfig import DATASET_PATH

import os
import joblib


# if you don't have it, install spacy and run `python -m spacy download en_core_web_md`
print("Loading spaCy model...")
nlp = spacy.load("en_core_web_md")


print("Loading chatbot dataset...")
with open("data/chatbot.csv", "r") as g:
    lines = list(csv.reader(g))
    lineCount = 0
    for i in reversed(range(len(lines))):
        if not (lines[i][0] and lines[i][1]):
            print(f"WARNING: {lines[i]} skipped due to missing data")
            del lines[i]
    data = lines[2:] # list slicing to filter out headings


with open("data/chatbot_randomized_responses.csv", "r") as g:
    lines = list(csv.reader(g))
    lineCount = 0
    for i in reversed(range(len(lines))):
        if not (lines[i][0] and lines[i][1]):
            print(f"WARNING: {lines[i]} skipped due to missing data")
            del lines[i]
    randomized_responses = lines[2:] # list slicing to filter out headings


if os.path.exists("data/data_doc.joblib"):
    print("Loading preprocessed data...")
    data_doc = joblib.load("data/data_doc.joblib")
else:
    print("Analyzing chatbot dataset with spaCy...")
    data_humansays_only = [line[0] for line in data]
    data_doc = list(nlp.pipe(data_humansays_only))
    joblib.dump(data_doc, "data/data_doc.joblib")


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


if os.path.exists("data/movie_similarity.joblib") and os.path.exists("data/movie_vectors.joblib"):
    print("Loading preprocessed data...")
    similarity = joblib.load("data/movie_similarity.joblib")
    movie_vectors = joblib.load("data/movie_vectors.joblib")
else:
    print("Analyzing movie dataset with spaCy...")
    movies["combined_info"] = movies["title"] + movies["genres"] + movies["tags"]
    # TODO test which components can be disabled
    movie_pipe = nlp.pipe(movies["combined_info"], disable=["parser", "tagger", "lemmatizer", "senter"], n_process=-1)
    movie_doc = list(movie_pipe)
    movie_vectors = pd.DataFrame([doc.vector for doc in movie_doc])
    similarity = linear_kernel(movie_vectors, movie_vectors)
    movies = movies.drop(["combined_info"], axis=1)
    joblib.dump(similarity, "data/movie_similarity.joblib")
    joblib.dump(movie_vectors, "data/movie_vectors.joblib")


try:
    file = open('movie_history.csv', 'r')
except IOError:
    file = open('movie_history.csv', 'w')

with open('movie_history.csv', 'r') as f:
    movie_history = list(csv.reader(f))


def save_to_movie_history(movie_id: int):
    with open('movie_history.csv', 'a', newline='') as f:
        newFileWriter = csv.writer(f)
        newFileWriter.writerow(["0", movie_id])
