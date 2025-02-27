import math
import pickle
from collections import defaultdict
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')


class BM25:
    def __init__(self, documents, k1=1.5, b=0.75):
        self.documents = documents  # list of text documents
        self.k1 = k1
        self.b = b
        self.N = len(documents)
        self.doc_lengths = []
        self.avg_doc_length = 0
        self.index = defaultdict(list)  # mapping word -> list of (doc_index, term_frequency)
        self.idf = {}

        self._build_index()

    def _build_index(self):
        """Build the inverted index and compute IDF values."""
        doc_freqs = defaultdict(int)
        total_length = 0

        for i, doc in enumerate(self.documents):
            words = word_tokenize(doc.lower())
            self.doc_lengths.append(len(words))
            total_length += len(words)
            # Count term frequencies per document
            word_counts = defaultdict(int)
            for word in words:
                word_counts[word] += 1
            # For each unique word, update the index and document frequency
            for word, tf in word_counts.items():
                doc_freqs[word] += 1
                self.index[word].append((i, tf))

        self.avg_doc_length = total_length / self.N

        # Compute IDF for each word
        for word, df in doc_freqs.items():
            self.idf[word] = math.log((self.N - df + 0.5) / (df + 0.5) + 1)

    def search(self, query, top_n=5):
        """Score the documents given a query and return the top_n document indices and scores."""
        query_words = word_tokenize(query.lower())
        scores = defaultdict(float)

        for word in query_words:
            if word not in self.index:
                continue

            idf = self.idf.get(word, 0)
            for doc_id, tf in self.index[word]:
                dl = self.doc_lengths[doc_id]
                score = idf * ((tf * (self.k1 + 1)) /
                               (tf + self.k1 * (1 - self.b + self.b * (dl / self.avg_doc_length))))
                scores[doc_id] += score

        # Return a sorted list of (doc_id, score)
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def save(self, index_file="bm25_index.pkl"):
        """Save the BM25 index along with the document lengths and idf values."""
        with open(index_file, "wb") as f:
            pickle.dump({
                "index": self.index,
                "doc_lengths": self.doc_lengths,
                "avg_doc_length": self.avg_doc_length,
                "idf": self.idf,
                "N": self.N,
                "documents": self.documents,
                "k1": self.k1,
                "b": self.b,
            }, f)

    @staticmethod
    def load(index_file="bm25_index.pkl"):
        """Load the BM25 index from file and return a BM25 instance."""
        with open(index_file, "rb") as f:
            data = pickle.load(f)
        bm25 = BM25(data["documents"], k1=data["k1"], b=data["b"])
        bm25.index = data["index"]
        bm25.doc_lengths = data["doc_lengths"]
        bm25.avg_doc_length = data["avg_doc_length"]
        bm25.idf = data["idf"]
        bm25.N = data["N"]
        return bm25
