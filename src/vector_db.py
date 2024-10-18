import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorDB:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []

    def add_to_db(self, text, chunk_size=1000):
        new_chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        embeddings = self.model.encode(new_chunks)
        self.index.add(np.array(embeddings).astype('float32'))
        self.chunks.extend(new_chunks)

    def retrieve_similar_chunks(self, query, k=5):  # Reduced from 5 to 2
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), k)
        return [self.chunks[i] for i in indices[0]]

# Usage
# vector_db = VectorDB()
# vector_db.add_to_db(paper_text)
# relevant_chunks = vector_db.retrieve_similar_chunks(query)