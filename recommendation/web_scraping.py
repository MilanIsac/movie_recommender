from pymongo import MongoClient
import requests
import os
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
if not API_KEY:
    raise ValueError("TMDB_API_KEY environment variable is not set")

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
collection = db[os.getenv("MONGO_COLLECTION")]

session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)

def fetch_movies(endpoint, pages=5, delay=0.5):
    inserted_count = 0
    for page in range(1, pages + 1):
        url = f"https://api.themoviedb.org/3/movie/{endpoint}?api_key={API_KEY}&language=en-US&page={page}"
        try:
            response = session.get(url, timeout=10).json()
            movies = response.get("results", [])
            
            for movie in movies:
                
                movie_doc = {
                    "id": movie["id"],
                    "title": movie["title"],
                    "overview": movie.get("overview", ""),
                    "genre_ids": movie.get("genre_ids", []),
                    "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
                    "release_date": movie.get("release_date", ""),
                    "vote_average": movie.get("vote_average", 0),
                    "vote_count": movie.get("vote_count", 0)
                }
                
                result = collection.update_one(
                    {"id": movie_doc["id"]},
                    {"$set": movie_doc},
                    upsert=True
                )
                if result.upserted_id:
                    inserted_count += 1
                    
                    
            time.sleep(delay)
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
    return inserted_count

if __name__ == "__main__":
    inserted_total = 0
    inserted_total += fetch_movies("popular", pages=10)
    inserted_total += fetch_movies("now_playing", pages=10)
    inserted_total += fetch_movies("upcoming", pages=10)

    print(f"Inserted {inserted_total} new movies into MongoDB")
    print("Movies in DB:", collection.count_documents({}))
    latest_movies = list(collection.find().sort("release_date", -1).limit(5))

