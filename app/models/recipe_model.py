from pydantic import BaseModel

class Recipe(BaseModel):
    title: str
    ingredients: list
    instructions: str
    cuisine: str
    rating: float
    reviews: int
