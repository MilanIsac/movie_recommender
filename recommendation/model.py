from fastapi import FastAPI, HTTPException
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

# Load movies data
movies = pd.read_csv("movies.csv").fillna("")
movies['metadata'] = movies['genres'] + ' ' + movies['title'] + ' ' + movies['tagline']

# Initialize TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(movies['metadata'])
similarity_matrix = cosine_similarity(tfidf_matrix)


def recommend(name, top_n=5):
    if name not in movies['title'].values:
        raise HTTPException(status_code=404, detail="Movie not found")

    index = movies[movies['title'] == name].index[0]
    similarity_scores = list(enumerate(similarity_matrix[index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    top_movies = similarity_scores[1:top_n + 1]

    recommended_movies = []
    for i, score in top_movies:
        movie = movies.iloc[i].to_dict()
        # Parse genres if it's a JSON string
        if isinstance(movie["genres"], str) and movie["genres"].startswith("["):
            try:
                genres_list = json.loads(movie["genres"])
                # Extract only the name field from each genre object
                genres = [{"name": genre["name"]} for genre in genres_list if "name" in genre]
            except json.JSONDecodeError:
                genres = [{"name": g.strip()} for g in movie["genres"].split(",") if g]
        else:
            genres = [{"name": g.strip()} for g in movie["genres"].split(",") if g]

        recommended_movies.append({
            "title": movie["title"],
            "genres": genres,
            "tagline": movie["tagline"] if movie["tagline"] and pd.notna(movie["tagline"]) else "No tagline available",
            "similarity_score": float(score),
            "overview": movie["overview"] if movie["overview"] and pd.notna(movie["overview"]) else "No overview available",
            "vote_average": float(movie["vote_average"]) if pd.notna(movie["vote_average"]) else 0.0,
            "vote_count": int(movie["vote_count"]) if pd.notna(movie["vote_count"]) else 0
        })

    return recommended_movies

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/recommend/{name}")
def get_recommendations(name: str):
    recommendations = recommend(name)
    return {"recommendations": recommendations}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)