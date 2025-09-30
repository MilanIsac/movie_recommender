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

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
collection = db[os.getenv("MONGO_COLLECTION")]

# Setup requests session with retries
session = requests.Session()
retry = Retry(
    total=5,  # total retry attempts
    backoff_factor=1,  # wait 1s, 2s, 4s...
    status_forcelist=[500, 502, 503, 504]  # retry on these HTTP codes
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

for movie in collection.find().limit(5):
    print(movie)


inserted_total = 0
inserted_total += fetch_movies("popular", pages=10)
inserted_total += fetch_movies("now_playing", pages=10)
inserted_total += fetch_movies("upcoming", pages=10)

print(f"Inserted {inserted_total} new movies into MongoDB")



# # Connect to your MongoDB Atlas cluster
# client = MongoClient(os.getenv("MONGO_URI"))
# db = client[os.getenv("MONGO_DB")]
# collection = db[os.getenv("MONGO_COLLECTION")]

# # Fetch and print the first 5 movies
# for movie in collection.find().limit(5):
#     print(f"Title: {movie.get('title')}")
#     print(f"Overview: {movie.get('overview')}")
#     print(f"Release Date: {movie.get('release_date')}")
#     print(f"Vote Average: {movie.get('vote_average')}")
#     print("-" * 50)
