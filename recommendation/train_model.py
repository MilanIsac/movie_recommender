import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pickle

def train():
    df = pd.read_csv("movies.csv")

    tfidf = TfidfVectorizer(stop_words="english")
    df["overview"] = df["overview"].fillna("")
    tfidf_matrix = tfidf.fit_transform(df["overview"])

    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    with open("cosine_sim.pkl", "wb") as f:
        pickle.dump(cosine_sim, f)

    df.to_csv("movies.csv", index=False)
    print("✅ Model trained and cosine similarity saved")

if __name__ == "__main__":
    train()
