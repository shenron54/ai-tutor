import PyPDF2
import requests
from io import BytesIO
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import re
import scholarly

# TODO: Add functionality to accept URLs 
def extract_text_from_pdf(pdf_path):
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Example usage
pdf_path = "2307.07924v5.pdf"
paper_text = extract_text_from_pdf(pdf_path)


# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create a FAISS index
dimension = 384  # Depends on the model you're using
index = faiss.IndexFlatL2(dimension)

def add_to_vector_db(text, chunk_size=1000):
    # Split the text into chunks
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    # Encode the chunks
    embeddings = model.encode(chunks)
    
    # Add to the FAISS index
    index.add(np.array(embeddings).astype('float32'))
    
    return chunks

# Add the extracted text to the vector database
chunks = add_to_vector_db(paper_text)

def retrieve_similar_chunks(query, k=5):
    # Encode the query
    query_vector = model.encode([query])
    
    # Search the index
    distances, indices = index.search(np.array(query_vector).astype('float32'), k)
    
    # Return the most similar chunks
    return [chunks[i] for i in indices[0]]

# Example usage
query = "What is the main contribution of this paper?"
relevant_chunks = retrieve_similar_chunks(query)

def extract_citations(text):
    # This is a simple regex pattern and might need to be adjusted based on the citation format
    citation_pattern = r'\[(\d+)\]'
    return re.findall(citation_pattern, text)

def search_and_download_paper(citation):
    search_query = scholarly.search_pubs_query(citation)
    paper = next(search_query)
    if paper.bib.get('url'):
        return extract_text_from_pdf(paper.bib['url'])
    return None

# In your main processing loop:
citations = extract_citations(paper_text)
for citation in citations:
    cited_paper_text = search_and_download_paper(citation)
    if cited_paper_text:
        add_to_vector_db(cited_paper_text)