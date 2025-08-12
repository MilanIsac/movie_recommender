import time
import random
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client["movieDB"]
collection = db["movies"]

# IMDb scraping function
def scrape_imdb_movies(pages=5, delay_range=(2, 5)):
    base_url = "https://www.imdb.com/search/title/?title_type=feature&sort=release_date,desc&start={}&ref_=adv_nxt"

    for page in range(1, pages * 50 + 1, 50):
        url = base_url.format(page)
        print(f"Scraping page: {url}")
        
        # Fetch page
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find all movie containers
        movies = soup.find_all("div", class_="lister-item mode-advanced")
        
        for movie in movies:
            title_tag = movie.h3.a
            title = title_tag.text if title_tag else None

            year_tag = movie.h3.find("span", class_="lister-item-year text-muted unbold")
            year = year_tag.text if year_tag else None

            desc_tag = movie.find_all("p", class_="text-muted")
            description = desc_tag[1].text.strip() if len(desc_tag) > 1 else None

            rating_tag = movie.find("div", class_="inline-block ratings-imdb-rating")
            rating = rating_tag["data-value"] if rating_tag else None

            poster_tag = movie.find("img")
            poster_url = poster_tag["loadlate"] if poster_tag and "loadlate" in poster_tag.attrs else None

            # Save to MongoDB
            if title:
                movie_data = {
                    "title": title,
                    "year": year,
                    "description": description,
                    "rating": rating,
                    "poster_url": poster_url
                }
                collection.update_one({"title": title}, {"$set": movie_data}, upsert=True)
        
        # Random delay to avoid being blocked
        delay = random.uniform(*delay_range)
        print(f"Sleeping for {delay:.2f} seconds...\n")
        time.sleep(delay)

if __name__ == "__main__":
    scrape_imdb_movies(pages=10, delay_range=(3, 7))  # Scrape 10 pages (500 movies)
    print("Scraping completed and data stored in MongoDB.")
