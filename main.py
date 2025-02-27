import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from fastapi import FastAPI
from app.routes import recipes, bm25_search

app = FastAPI()

# Include the routes
app.include_router(recipes.router)
app.include_router(bm25_search.router)  # Register BM25 search

@app.get("/")
def read_root():
    return {"message": "Welcome to the Food Recipes API!"}
