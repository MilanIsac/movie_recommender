import json
from pymongo import MongoClient
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('MONGO_DB')]
collection = db[os.getenv('MONGO_COLLECTION')]

with open("movies.json", "r", encoding="utf-8") as f:
    data = json.load(f)

movies = data["results"]

# Insert into MongoDB
for movie in movies:
    collection.update_one({"id": movie["id"]}, {"$set": movie}, upsert=True)

# Save to CSV for debugging
pd.DataFrame(movies).to_csv("movies.csv", index=False)

print(f"✅ Inserted {len(movies)} movies into MongoDB")
