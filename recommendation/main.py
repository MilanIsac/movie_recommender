from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import pandas as pd
import pickle
from fastapi.middleware.cors import CORSMiddleware
from difflib import get_close_matches

load_dotenv()

app = FastAPI(title="Movie Recommendation API")

# ✅ Allow frontend (React) requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can change this later to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
collection = db[os.getenv("MONGO_COLLECTION")]

# ✅ Load model files safely
try:
    vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))
    similarity = pickle.load(open("model/similarity.pkl", "rb"))
    movie_index = pd.read_csv("model/movie_index.csv")

    # convert to lowercase once to avoid repeated conversion
    movie_index["title"] = movie_index["title"].str.strip().str.lower()

    print("✅ Model and data loaded successfully")
except Exception as e:
    print("❌ Error loading model:", e)
    raise e


@app.get("/")
async def home():
    return {"message": "🎬 FastAPI Movie Recommendation Service is running!"}


@app.get("/api/recommend/{title}")
async def recommend(title: str):
    # normalize to lowercase
    title = title.strip().lower()

    # If movie not in CSV, suggest closest matches
    if title not in movie_index["title"].values:
        suggestions = get_close_matches(title, movie_index["title"].tolist(), n=3, cutoff=0.5)
        if suggestions:
            raise HTTPException(
                status_code=404,
                detail=f"Movie '{title}' not found. Did you mean: {', '.join(suggestions)}?"
            )
        else:
            raise HTTPException(status_code=404, detail=f"Movie '{title}' not found in dataset")

    # get movie index safely
    idx = movie_index[movie_index["title"] == title].index[0]

    # calculate similarity
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:6]
    similar_movies = [movie_index.iloc[i]["title"] for i, _ in sim_scores]

    # fetch details from MongoDB (case-insensitive)
    results = list(collection.find({"title": {"$in": [t for t in similar_movies]}}, {"_id": 0}))

    # fill missing ones
    found_titles = {m["title"].lower() for m in results}
    for t in similar_movies:
        if t not in found_titles:
            results.append({"title": t, "overview": "Not available in DB"})

    return {"base_movie": title, "recommendations": results}
