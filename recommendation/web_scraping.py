import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]


def fetch_movies(category="popular", pages=5):
    print(f"📥 Fetching TMDB movies: {category}")

    for page in range(1, pages + 1):
        url = f"https://api.themoviedb.org/3/movie/{category}"
        params = {
            "api_key": TMDB_API_KEY,
            "page": page
        }

        res = requests.get(url, params=params)
        res.raise_for_status()

        for movie in res.json().get("results", []):
            movie["source"] = "tmdb"
            movie["updated_at"] = datetime.utcnow()

            collection.update_one(
                {"id": movie["id"]},
                {"$set": movie},
                upsert=True
            )

    print("✅ TMDB fetch completed")
