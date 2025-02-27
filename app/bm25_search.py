from flask import Blueprint, request, jsonify
import pickle
from ..indexer.bm25 import BM25

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
    top_n = int(request.args.get('top_n', 5))

    if not query:
        return jsonify({"error": "Query parameter is missing"}), 400

    # Load BM25 index
    bm25, recipe_ids = load_bm25_index()

    # Perform the search
    results = bm25.search(query, top_n)

    # Map result to recipe_ids
    search_results = [
        {"recipe_id": recipe_ids[doc_id], "score": score}
        for doc_id, score in results
    ]

    return jsonify({"results": search_results})
