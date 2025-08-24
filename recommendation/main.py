import os
import requests
from fastapi import FastAPI
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

TMDB_API_KEY = os.getenv("API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# TMDB base URL
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow Node.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "🎬 TMDB + MongoDB API is running!"}


@app.get("/fetch-movies")
def fetch_movies():
    """Fetch movies from TMDB (with full details) and save to MongoDB"""
    all_movies = []
    for page in range(1, 3):  # adjust number of pages
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page={page}"
        response = requests.get(url)

        if response.status_code != 200:
            return {"error": f"❌ Failed to fetch page {page}"}

        movies = response.json().get("results", [])

        for movie in movies:
            movie_id = movie["id"]

            # Fetch full details (tagline, genres, runtime, etc.)
            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
            details_res = requests.get(details_url)

            if details_res.status_code == 200:
                details = details_res.json()
                movie.update({
                    "tagline": details.get("tagline", ""),
                    "genres": details.get("genres", []),
                    "runtime": details.get("runtime", 0),
                    "release_date": details.get("release_date", ""),
                    "poster_full": TMDB_IMAGE_BASE + details["poster_path"] if details.get("poster_path") else None
                })

            # Save to MongoDB
            collection.update_one({"id": movie["id"]}, {"$set": movie}, upsert=True)

            all_movies.append(movie)

    return {"message": f"✅ Inserted/Updated {len(all_movies)} movies into MongoDB"}


@app.get("/movies")
def get_movies(limit: int = 10):
    """Retrieve movies from MongoDB (with pagination)"""
    data = list(collection.find({}, {"_id": 0}).limit(limit))
    return {"count": len(data), "movies": data}


@app.get("/movie/{movie_id}")
def get_movie(movie_id: int):
    """Get a single movie by ID"""
    movie = collection.find_one({"id": movie_id}, {"_id": 0})
    if not movie:
        return {"error": "Movie not found"}
    return movie
