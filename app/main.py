from fastapi import FastAPI
from app.routes import recipes  # Importing the routes for recipes

app = FastAPI()

# Including the routes
app.include_router(recipes.router)

# You can also run the FastAPI app with Uvicorn programmatically
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
