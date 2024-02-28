import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import re


DATASET_PATH = "data/ml-latest-small/"


def random_movie() -> str:
    return "placeholder"

def search_movie() -> str:
    return "placeholder"

def recommend_movie() -> str:
    return "placeholder"

def movie_menu(movie_id: int) -> str:
    response = "You've chosen movie ID: " + str(movie_id) + " from the menu."
    response += " I'm still working on this feature."
    return response
