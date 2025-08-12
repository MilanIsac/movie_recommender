import requests
from bs4 import BeautifulSoup
import pymongo
from datetime import datetime

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['movies']
collection = db['latest_movies']

url = "https://www.imdb.com/search/title/?title_type=feature&sort=release_date,desc"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

added_count = 0

for movie in soup.select('.lister-item.mode-advanced'):
    title = movie.h3.a.text.strip()
    year = movie.find('span', class_='lister-item-year').text.strip('()')
    rating = movie.find('div', class_='inline-block ratings-imdb-rating').strong.text
    description = movie.find_all('p', class_='text_muted')[1].text.strip()
    poster_url = movie.find('img')['loadlate']
    
    if collection.find_one({'title': title, 'year': year}):
        print(f'Skipping (already in db): {title}')
        continue
    
    movie_data = {
        'title': title,
        'year': year,
        'rating': rating,
        'description': description,
        'added_at': datetime.timezone.utc
    }
    
    collection.insert_one(movie_data)
    print(f'Added: {title}')
    added_count += 1
    
print(f'\nScraping completed {added_count} new movies added')