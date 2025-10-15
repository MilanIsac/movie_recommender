# train_model.py
import os
from pymongo import MongoClient
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
collection = db[os.getenv("MONGO_COLLECTION")]

print("✅ Connected to MongoDB")

# Load movie data
movies = list(collection.find())
df = pd.DataFrame(movies)
print(f"✅ Loaded {len(df)} movies")

# Clean and combine text features
def combine_features(row):
    overview = row.get("overview", "")
    genres = ""
    if isinstance(row.get("genres"), list):
        genres = " ".join([g["name"] for g in row["genres"] if isinstance(g, dict)])
    elif isinstance(row.get("genre_ids"), list):
        genres = " ".join(map(str, row["genre_ids"]))
    return f"{overview} {genres}"

df["combined"] = df.apply(combine_features, axis=1)

# Remove missing values
df = df.dropna(subset=["combined"])

# TF-IDF Vectorizer
print("🔧 Vectorizing text...")
vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
tfidf_matrix = vectorizer.fit_transform(df["combined"])

# Compute cosine similarity matrix
print("⚙️ Computing similarity...")
similarity_matrix = cosine_similarity(tfidf_matrix)

# Save model + data
os.makedirs("model", exist_ok=True)
pickle.dump(vectorizer, open("model/vectorizer.pkl", "wb"))
pickle.dump(similarity_matrix, open("model/similarity.pkl", "wb"))
df[["id", "title"]].to_csv("model/movie_index.csv", index=False)

print("✅ Model training complete!")
print("Files saved in ./model/")
