from flask import Blueprint, request, jsonify
import pickle
from bm25 import BM25

# Load BM25 index from pickle
def load_bm25_index():
    with open('pickle/bm25_index.pkl', 'rb') as f:
        data = pickle.load(f)
    bm25 = data["bm25"]
    recipe_ids = data["recipe_ids"]
    return bm25, recipe_ids

# Define search endpoint
bm25_search = Blueprint('bm25_search', __name__)

@bm25_search.route("/search", methods=["GET"])
def search():
    query = request.args.get('query', '')
    top_n = int(request.args.get('top_n', 10))  # Default to top 10 if no 'top_n' is specified

    if not query:
        query = "default"  # Use a placeholder query if query is missing

    # Load BM25 index
    bm25, recipe_ids = load_bm25_index()

    # Debug: Check the loaded BM25 index size and first few entries
    print(f"Loaded BM25 index with {len(recipe_ids)} documents.")
    print(f"First 5 recipe_ids: {recipe_ids[:5]}")

    # Perform the search
    results = bm25.search(query, top_n)
    print(f"Search results for query '{query}':", results)

    # Map result to recipe_ids
    search_results = [
        {"recipe_id": recipe_ids[doc_id], "score": score}
        for doc_id, score in results
    ]

    # Check if search_results is empty and return a message if no results were found
    if not search_results:
        return jsonify({"message": "No results found"}), 404

    return jsonify({"results": search_results})
