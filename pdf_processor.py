import PyPDF2
import requests
from io import BytesIO

def extract_text_from_pdf(pdf_url):
    response = requests.get(pdf_url)
    pdf_file = BytesIO(response.content)
    
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    return text