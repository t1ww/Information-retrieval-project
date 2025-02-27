from flask import Flask
from bm25_search import bm25_search

app = Flask(__name__)

# Register the search blueprint
app.register_blueprint(bm25_search)

if __name__ == "__main__":
    app.run(debug=True)
