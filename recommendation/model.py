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

# def recommend(name, top_n=5):
#     """
#     Recommend movies based on the given movie name.
#     """
#     # Check if the movie exists in the dataset
#     if name not in movies['title'].values:
#         raise HTTPException(status_code=404, detail="Movie not found")

#     # Get the index of the movie
#     index = movies[movies['title'] == name].index[0]

#     # Get the similarity scores for the movie
#     similarity_scores = list(enumerate(similarity_matrix[index]))

#     # Sort movies by similarity score
#     similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

#     # Get the top N similar movies (excluding the movie itself)
#     top_movies = similarity_scores[1:top_n + 1]

#     # Prepare the recommended movies
#     recommended_movies = []
#     for i, score in top_movies:
#         movie = movies.iloc[i].to_dict()
#         print("Raw genres:", movie["genres"])
#         recommended_movies.append({
#             "title": movie["title"],
#             "genres": [{"name" : g.strip()} for g in movie["genres"]. split(",") if g],
#             "tagline": movie["tagline"],
#             "similarity_score": float(score)  # Convert numpy float to Python float
#         })

#     return recommended_movies

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
                # Fallback to splitting by comma if JSON parsing fails
                genres = [{"name": g.strip()} for g in movie["genres"].split(",") if g]
        else:
            # If it's not a JSON string, split by comma
            genres = [{"name": g.strip()} for g in movie["genres"].split(",") if g]

        recommended_movies.append({
            "title": movie["title"],
            "genres": genres,
            "tagline": movie["tagline"] if movie["tagline"] and pd.notna(movie["tagline"]) else "No tagline available",
            "similarity_score": float(score),
            "overview": movie["overview"] if movie["overview"] and pd.notna(movie["overview"]) else "No overview available",  # Add overview
            "vote_average": float(movie["vote_average"]) if pd.notna(movie["vote_average"]) else 0.0,  # Add vote_average
            "vote_count": int(movie["vote_count"]) if pd.notna(movie["vote_count"]) else 0  # Add vote_count
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
    """
    Endpoint to get movie recommendations based on the given movie name.
    """
    recommendations = recommend(name)
    return {"recommendations": recommendations}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)