from fastapi import FastAPI, HTTPException, BackgroundTasks
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import pandas as pd
import pickle
from fastapi.middleware.cors import CORSMiddleware
from difflib import get_close_matches
import time
from mangum import Mangum
import numpy as np

from pydantic import BaseModel


class MovieRequest(BaseModel):
    movies: list[str]


load_dotenv()

app = FastAPI(title="Movie Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
collection = db[os.getenv("MONGO_COLLECTION")]

try:
    vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))
    similarity = pickle.load(open("model/similarity.pkl", "rb"))
    movie_index = pd.read_csv("model/movie_index.csv")

    movie_index["title"] = movie_index["title"].str.strip().str.lower()

    print("Model and data loaded successfully")

except Exception as e:
    print("Error loading model:", e)
    raise e


def run_scraping():
    from web_scraping import fetch_movies

    fetch_movies("popular", pages=5)
    print("Web scraping completed!")


def run_model_training():
    import model

    print("Model training completed")


@app.get("/")
async def home():
    return {"message": "FastAPI Movie Recommendation Service is running!"}


# @app.get("/api/recommend/{title}")
# async def recommend(title: str):
#     title = title.strip().lower()
#     titles = movie_index["title"].tolist()

#     if title not in titles:
#         suggestions = get_close_matches(title, titles, n=3, cutoff=0.4)
#         if suggestions:
#             best_match = suggestions[0]
#             print(f"Using closest match: {best_match}")
#             title = best_match
#         else:
#             raise HTTPException(
#                 status_code=404, detail=f"Movie '{title}' not found in dataset."
#             )

#     idx = movie_index[movie_index["title"] == title].index[0]

#     sim_scores = list(enumerate(similarity[idx]))
#     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[0:11]
#     similar_movies = [movie_index.iloc[i]["title"] for i, _ in sim_scores]

#     results = []
#     for t in similar_movies:
#         movie_doc = collection.find_one(
#             {"title": {"$regex": f"^{t}$", "$options": "i"}}, {"_id": 0}
#         )
#         if movie_doc:
#             poster = movie_doc.get("poster_path")
#             if poster and not poster.startswith("http"):
#                 movie_doc["poster_path"] = f"https://image.tmdb.org/t/p/w500{poster}"
#             results.append(movie_doc)
#         found_titles = {m["title"].lower() for m in results}
#     for t in similar_movies:
#         if t not in found_titles:
#             results.append({"title": t, "overview": "Not available in DB"})

#     return {"base_movie": title, "recommendations": results}


@app.post("/api/recommend")
async def recommend_movies(request: MovieRequest):
    movie_list = request.movies

    if len(movie_list) == 0:
        raise HTTPException(status_code=400, detail="No movies provided")

    titles = movie_index["title"].tolist()
    indices = {title: i for i, title in enumerate(titles)}

    combined_scores = np.zeros(len(similarity))
    matched_movies = []

    for m in movie_list:
        m = m.strip().lower()

        if m in indices:
            matched_movies.append(m)
        else:
            close = get_close_matches(m, titles, n=1, cutoff=0.4)
            if close:
                print(f"Using fuzzy match: {m} → {close[0]}")
                matched_movies.append(close[0])
            else:
                print(f"No match for: {m}")
                continue

        idx = indices[matched_movies[-1]]
        sim_scores = list(enumerate(similarity[idx]))

        for i, score in sim_scores:
            combined_scores[i] += score

    if combined_scores.sum() == 0:
        return {
            "matched_movies": [],
            "recommendations": []
        }


    sorted_indices = combined_scores.argsort()[::-1]
    filtered = [i for i in sorted_indices if titles[i] not in matched_movies]
    top_movies = movie_index.iloc[filtered][:10].to_dict(orient="records")

    GENRE_MAP = {
        28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
        80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
        14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
        9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
        10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
    }

    final_results = []

    for movie in top_movies:
        title = movie["title"]

        doc = collection.find_one(
            {"title": {"$regex": f"^{title}$", "$options": "i"}}, {"_id": 0}
        )

        if doc:
            if doc.get("poster_path") and not doc["poster_path"].startswith("http"):
                doc["poster_path"] = f"https://image.tmdb.org/t/p/w500{doc['poster_path']}"

            if not doc.get("overview"):
                doc["overview"] = "No overview available."

            genre_ids = doc.get("genre_ids", [])
            valid_genres = [GENRE_MAP.get(g) for g in genre_ids if GENRE_MAP.get(g)]
            doc["genres"] = valid_genres if valid_genres else ["Unknown"]

            final_results.append(doc)

        else:
            movie["overview"] = "Not available in DB"
            movie["genres"] = ["Unknown"]
            final_results.append(movie)

    return {
        "matched_movies": matched_movies,
        "recommendations": final_results
    }


@app.post("/api/refresh")
async def refresh(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(run_scraping)
        return {"msg": "fetching data started"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching data")


@app.post("/api/run-training")
async def run_training(background_tasks: BackgroundTasks):
    try:
        import model

        time.sleep(2)
        background_tasks.add_task(run_model_training)
        background_tasks.add_task(model_reload)
        return {"msg": "model training and reload started"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error training model")


async def model_reload():
    global vectorizer, similarity, movie_index
    try:
        vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))
        similarity = pickle.load(open("model/similarity.pkl", "rb"))
        movie_index = pd.read_csv("model/movie_index.csv")
        movie_index["title"] = movie_index["title"].str.strip().str.lower()
        print("Model reloaded successfully")
    except Exception as e:
        print("Error reloading model:", e)


handler = Mangum(app)
