import os
from pymongo import MongoClient
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
collection = db[os.getenv("MONGO_COLLECTION")]

print("Connected to MongoDB")

movies = list(collection.find())
df = pd.DataFrame(movies)
print(f"Loaded {len(df)} movies")

def combine_features(row):
    overview = row.get("overview", "")
    genres = ""
    if isinstance(row.get("genres"), list):
        genres = " ".join([g["name"] for g in row["genres"] if isinstance(g, dict)])
    elif isinstance(row.get("genre_ids"), list):
        genres = " ".join(map(str, row["genre_ids"]))
    return f"{overview} {genres}"

df["combined"] = df.apply(combine_features, axis=1)

df = df.dropna(subset=["combined"])

print("Movies loaded for training:", len(df))
print(df.tail()[["title", "release_date"]])


print("Vectorizing text...")
vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
tfidf_matrix = vectorizer.fit_transform(df["combined"])

print("Computing similarity...")
similarity_matrix = cosine_similarity(tfidf_matrix)

os.makedirs("model", exist_ok=True)
pickle.dump(vectorizer, open("model/vectorizer.pkl", "wb"))
pickle.dump(similarity_matrix, open("model/similarity.pkl", "wb"))
df[["id", "title"]].to_csv("model/movie_index.csv", index=False)

print("Model training complete!")
print("Files saved in ./model/")
