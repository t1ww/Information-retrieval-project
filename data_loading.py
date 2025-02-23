import pandas as pd
from pymongo import MongoClient
import numpy as np

def convert_np_arrays(record):
    for key, value in record.items():
        if isinstance(value, np.ndarray):
            record[key] = value.tolist()
    return record

# Connect to MongoDB (ensure mongod is running)
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client['food_recipes']

# Load recipes data from Parquet file
recipes_df = pd.read_parquet('resource/recipes.parquet')
recipes_data = recipes_df.to_dict('records')

# Convert numpy arrays in recipes_data to lists
recipes_data = [convert_np_arrays(rec) for rec in recipes_data]

# Insert recipes data into MongoDB
recipes_collection = db['recipes']
recipes_collection.insert_many(recipes_data)

# Load reviews data from Parquet file
reviews_df = pd.read_parquet('resource/reviews.parquet')
reviews_data = reviews_df.to_dict('records')

# Convert numpy arrays in reviews_data to lists (if any)
reviews_data = [convert_np_arrays(rec) for rec in reviews_data]

# Insert reviews data into MongoDB
reviews_collection = db['reviews']
reviews_collection.insert_many(reviews_data)

print("Data imported successfully!")
