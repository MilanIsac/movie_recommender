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
    print('Model training completed')


@app.get("/")
async def home():
    return {"message": "FastAPI Movie Recommendation Service is running!"}


@app.get("/api/recommend/{title}")
async def recommend(title: str):
    title = title.strip().lower()
    titles = movie_index["title"].tolist()

    if title not in titles:
        suggestions = get_close_matches(title, titles, n=3, cutoff=0.4)
        if suggestions:
            best_match = suggestions[0]
            print(f"Using closest match: {best_match}")
            title = best_match
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Movie '{title}' not found in dataset."
            )

    idx = movie_index[movie_index["title"] == title].index[0]

    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:6]
    similar_movies = [movie_index.iloc[i]["title"] for i, _ in sim_scores]


    results = []
    for t in similar_movies:
        movie_doc = collection.find_one(
            {"title": {"$regex": f"^{t}$", "$options": "i"}}, {"_id": 0}
        )
        if movie_doc:
            poster = movie_doc.get("poster_path")
            if poster and not poster.startswith("http"):
                movie_doc["poster_path"] = f"https://image.tmdb.org/t/p/w500{poster}"
            results.append(movie_doc)
        found_titles = {m["title"].lower() for m in results}
    for t in similar_movies:
        if t not in found_titles:
            results.append({"title": t, "overview": "Not available in DB"})

    return {"base_movie": title, "recommendations": results}


@app.post('/api/refresh')
async def refresh(background_tasks : BackgroundTasks):
    try:
        background_tasks.add_task(run_scraping)
        return { 'msg' : 'fetching data started' }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail='Error fetching data')
    
    
@app.post('/api/run-training')
async def run_training(background_tasks: BackgroundTasks):
    try:
        import model
        time.sleep(2)
        background_tasks.add_task(run_model_training)
        background_tasks.add_task(model_reload)
        return { 'msg' : 'model training and reload started' }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail='Error training model')
    
    
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