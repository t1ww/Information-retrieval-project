from fastapi import APIRouter
from pymongo import MongoClient
from bson import ObjectId
from app.models.recipe_model import Recipe

router = APIRouter()

# Connect to MongoDB
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["food_recipes"]
recipes_collection = db["recipes"]

# Helper function to serialize MongoDB documents
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# Route to fetch recipes
@router.get("/recipes")
def get_recipes(limit: int = 5):
    recipes = list(recipes_collection.find().limit(limit))
    recipes = [serialize_doc(recipe) for recipe in recipes]
    return recipes

# Example for creating a new recipe (POST request)
@router.post("/recipes")
def create_recipe(recipe: Recipe):
    new_recipe = recipe.dict()
    result = recipes_collection.insert_one(new_recipe)
    return {"message": "Recipe created!", "id": str(result.inserted_id)}
