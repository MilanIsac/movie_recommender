import os
import pickle
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

MODEL_DIR = "model"
os.makedirs(MODEL_DIR, exist_ok=True)


def build_text(row):
    overview = row.get("overview", "") or ""
    genres = row.get("genres", [])
    genre_text = ""

    if isinstance(genres, list):
        genre_text = " ".join(
            g["name"] if isinstance(g, dict) else str(g) for g in genres
        )

    return f"{overview} {genre_text}".strip()


def train_model():
    print("🔄 Loading movies from MongoDB...")
    movies = list(collection.find({}, {"_id": 0}))

    if not movies:
        raise ValueError("No movies found in DB")

    df = pd.DataFrame(movies)
    df["title"] = df["title"].str.lower().str.strip()
    df["combined"] = df.apply(build_text, axis=1)
    df = df[df["combined"].str.len() > 0].reset_index(drop=True)

    print(f"🎬 Training on {len(df)} movies")

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=6000,
        ngram_range=(1, 2)
    )

    tfidf = vectorizer.fit_transform(df["combined"])
    similarity = cosine_similarity(tfidf)

    pickle.dump(vectorizer, open(f"{MODEL_DIR}/vectorizer.pkl", "wb"))
    pickle.dump(similarity, open(f"{MODEL_DIR}/similarity.pkl", "wb"))
    df[["id", "title"]].to_csv(f"{MODEL_DIR}/movie_index.csv", index=False)

    print("✅ Model training completed")


if __name__ == "__main__":
    train_model()
