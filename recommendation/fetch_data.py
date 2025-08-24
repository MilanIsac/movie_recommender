import os
import time
import random
import requests
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TMDB_API_KEY = os.getenv("API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY is missing in .env file")
if not MONGO_URI:
    raise ValueError("MONGO_URI is missing in .env file")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (compatible; MyMovieApp/1.0; +http://localhost)"
}

# def safe_request(url):
#     for attempt in range(5):  # max 5 retries
#         try:
#             res = requests.get(url, headers=HEADERS, timeout=10, verify=True)
#             res.raise_for_status()
#             return res.json()
#         except Exception as e:
#             wait = (2 ** attempt) + random.random()
#             print(f"⚠️ Request failed ({e}), retrying in {wait:.2f}s...")
#             time.sleep(wait)
#         time.sleep(2)
#     return None

session = requests.Session()
session.headers.update(HEADERS)

def safe_request(url):
    for attempt in range(5):
        try:
            res = session.get(url, timeout=10, verify=True)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            wait = (2 ** attempt) + random.random()
            print(f"⚠️ Request failed ({e}), retrying in {wait:.2f}s...")
            time.sleep(wait)
    return None



def fetch_movies():
    all_movies = []

    for page in range(1, 3):
        print(f"\n📄 Fetching page {page}...")
        # url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page={page}"
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page={page}"
        data = safe_request(url)
        if not data:
            continue

        for movie in data.get("results", []):
            movie_id = movie["id"]

            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
            details = safe_request(details_url)
            if details:
                movie.update({
                    "tagline": details.get("tagline", ""),
                    "genres": [g["name"] for g in details.get("genres", [])],
                    "runtime": details.get("runtime", 0),
                    "release_date": details.get("release_date") or "",
                    "poster_full": TMDB_IMAGE_BASE + details["poster_path"] if details.get("poster_path") else None
                })

            all_movies.append(movie)

            collection.update_one({"id": movie["id"]}, {"$set": movie}, upsert=True)

            time.sleep(random.uniform(1, 2))  # safe request pacing
  # ⏳ pause 5 sec between pages

    # Save to CSV
    if all_movies:
        df = pd.DataFrame(all_movies)
        df.to_csv("movies.csv", index=False)
        print(f"✅ Saved {len(all_movies)} movies to movies.csv")
        print(f"✅ Inserted/Updated {len(all_movies)} movies into MongoDB Atlas")
    else:
        print("❌ No movies fetched!")

if __name__ == "__main__":
    fetch_movies()
