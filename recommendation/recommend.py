import pickle
import pandas as pd
from difflib import get_close_matches

vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))
similarity = pickle.load(open("model/similarity.pkl", "rb"))
movie_index = pd.read_csv("model/movie_index.csv")

movie_index["title"] = movie_index["title"].str.lower().str.strip()
titles = movie_index["title"].tolist()
indices = {t: i for i, t in enumerate(titles)}


def recommend_movies(movie_list, top_n=10):
    combined_scores = [0.0] * len(titles)
    matched = []

    for m in movie_list:
        m = m.lower().strip()
        if m not in indices:
            close = get_close_matches(m, titles, n=1, cutoff=0.4)
            if not close:
                continue
            m = close[0]

        matched.append(m)
        idx = indices[m]

        for i, score in enumerate(similarity[idx]):
            combined_scores[i] += score

    ranked = sorted(
        enumerate(combined_scores),
        key=lambda x: x[1],
        reverse=True
    )

    results = []
    for i, _ in ranked:
        if titles[i] not in matched:
            results.append(titles[i])
        if len(results) == top_n:
            break

    return results
