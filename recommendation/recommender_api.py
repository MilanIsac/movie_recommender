from fastapi import FastAPI
from pymongo import MongoClient
import os, pickle
import pandas as pd
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow Node.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("cosine_sim.pkl", "rb") as f:
    cosine_sim = pickle.load(f)

movies_df = pd.read_csv("movies.csv")
indices = pd.Series(movies_df.index, index=movies_df["title"].str.lower()).drop_duplicates()

# @app.get("/api/recommend/{title}")
# def recommend(title: str):
#     title_lower = title.lower()
#     if title_lower not in indices:
#         return {"recommendations": []}

#     idx = indices[title_lower]
#     sim_scores = sorted(enumerate(cosine_sim[idx]), key=lambda x: x[1], reverse=True)
#     sim_indices = [i for i, score in sim_scores[1:6]]

#     # ⚡ Filter out indices that don't exist in movies_df
#     sim_indices = [i for i in sim_indices if i < len(movies_df)]

#     recommended = movies_df.iloc[sim_indices][["title"]].to_dict(orient="records")

#     for rec in recommended:
#         doc = collection.find_one({"title": rec["title"]}, {"_id": 0, "poster_full": 1, "tagline": 1})
#         if doc:
#             rec.update(doc)

#     return {"recommendations": recommended}

@app.get("/api/recommend/{title}")
def recommend(title: str):
    title_lower = title.lower()
    if title_lower not in indices:
        return {"recommendations": []}

    idx = indices[title_lower]
    sim_scores = sorted(enumerate(cosine_sim[idx]), key=lambda x: x[1], reverse=True)
    sim_indices = [i for i, score in sim_scores[1:6]]
    
    sim_indices = [i for i in sim_indices if i < len(movies_df)]


    recommended = movies_df.iloc[sim_indices][["title"]].to_dict(orient="records")

    for rec in recommended:
        doc = collection.find_one(
            {"title": rec["title"]},
            {
                "_id": 0,
                "poster_full": 1,
                "tagline": 1,
                "genres": 1,
                "overview": 1,
                "vote_average": 1,
                "vote_count": 1,
                "runtime": 1,
                "release_date": 1
            }
        )
        if doc:
            rec.update(doc)

    return {"recommendations": recommended}
