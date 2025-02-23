from fastapi import FastAPI
from app.routes import recipes

app = FastAPI()

# Include the routes for recipes
app.include_router(recipes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Food Recipes API!"}