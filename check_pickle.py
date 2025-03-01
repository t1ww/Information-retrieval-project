import pickle
from bm25 import BM25

# Load the pickle file
with open("pickle/bm25_index.pkl", "rb") as f:
    data = pickle.load(f)

# Inspect the contents of the loaded file
bm25 = data.get("bm25")
recipe_ids = data.get("recipe_ids")

# Check if BM25 and recipe_ids exist
if bm25 and recipe_ids:
    print("BM25 index loaded successfully.")
    print(f"Number of recipes: {len(recipe_ids)}")
else:
    print("Error loading BM25 index or recipe_ids.")
