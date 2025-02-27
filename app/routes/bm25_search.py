from fastapi import APIRouter, Query, HTTPException
from pymongo import MongoClient
import pickle
from ..indexer.bm25 import BM25

router = APIRouter()

# Load BM25 index (do this once at startup)
try:
    with open("pickle/bm25_index.pkl", "rb") as f:
        data = pickle.load(f)
    bm25 = data["bm25"]
    recipe_ids = data["recipe_ids"]
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error loading BM25 index: {e}")

# Connect to MongoDB (adjust URI if needed)
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client['food_recipes']

@router.get("/search/bm25")
def search_bm25(query: str = Query(..., description="Search query for recipes"), top_n: int = 5):
    results = bm25.search(query, top_n=top_n)
    # results is a list of tuples (doc_index, score)
    # Map document indices back to Mongo recipe IDs
    matched_ids = [recipe_ids[doc_idx] for doc_idx, score in results]

    # Retrieve full recipes from MongoDB using _id
    recipes = list(db.recipes.find({"_id": {"$in": matched_ids}}))
    # (Optional: you could sort recipes to match the order of matched_ids)

    return {"query": query, "results": recipes}
