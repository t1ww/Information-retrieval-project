from pymongo import MongoClient
from bm25 import BM25

import pickle
import os

# Connect to MongoDB
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client['food_recipes']

# Load recipes from MongoDB (adjust query as needed)
recipes = list(db.recipes.find({}))

# For each recipe, combine the desired text fields
documents = []
recipe_ids = []  # store the Mongo _id (as string) for later mapping
for recipe in recipes:
    # Adjust these keys to match your recipe schema
    text = recipe.get('title', '') + " " + recipe.get('ingredients', '') + " " + recipe.get('instructions', '')
    documents.append(text)
    recipe_ids.append(str(recipe['_id']))

# Build the BM25 index over the documents
bm25 = BM25(documents)

# Save the BM25 index along with the recipe id mapping
os.makedirs("pickle", exist_ok=True)
with open("pickle/bm25_index.pkl", "wb") as f:
    pickle.dump({
        "bm25": bm25,
        "recipe_ids": recipe_ids,
    }, f)

print("BM25 index built and saved.")
