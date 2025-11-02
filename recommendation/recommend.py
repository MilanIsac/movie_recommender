import pickle
import pandas as pd

vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))
similarity_matrix = pickle.load(open("model/similarity.pkl", "rb"))
movies = pd.read_csv("model/movie_index.csv")

def recommend(title, top_n=5):
    if title not in movies["title"].values:
        return f"Movie '{title}' not found."
    
    idx = movies[movies["title"] == title].index[0]
    sim_scores = list(enumerate(similarity_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    recommendations = [movies.iloc[i]["title"] for i, _ in sim_scores]
    return recommendations
