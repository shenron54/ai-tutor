import streamlit as st
from azure_client import AzureClient
from pdf_processor import extract_text_from_pdf
from vector_db import VectorDB
from chat_history import ChatHistory
import tiktoken
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

endpoint = "https://chatdevtestapi3.openai.azure.com/openai/deployments/ChatDevGPT/chat/completions?api-version=2024-08-01-preview"  # https://xyz.azure.com/
key = "c7191f13498741cd87a06cecb5fc01de"  # Your API key
model_name = "gpt-4o"  # Your model name

# Initialize components
azure_client = AzureClient(endpoint, key, model_name)
vector_db = VectorDB()
chat_history = ChatHistory()

st.title("AI Research Paper Tutor")

# previous_messages = chat_history.get_all_messages()
# for msg in previous_messages:
#     st.session_state.messages.append({"role": msg[1], "content": msg[2]})
    
# if st.button("Load Previous Chats"):
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])


# Add this function to your app.py
def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def truncate_to_token_limit(text: str, limit: int = 1000) -> str:
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    if len(tokens) <= limit:
        return text
    return encoding.decode(tokens[:limit])

# PDF URL input
pdf_url = st.text_input("Enter the URL of the research paper PDF:")
if pdf_url:
    paper_text = extract_text_from_pdf(pdf_url)
    vector_db.add_to_db(paper_text)
    st.success("Paper processed and added to the database!")

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to know about the research paper?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    chat_history.add_message("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # After retrieving relevant chunks
    relevant_chunks = vector_db.retrieve_similar_chunks(prompt)

    # Log the retrieved chunks
    logging.info("Retrieved chunks:")
    for i, chunk in enumerate(relevant_chunks):
        logging.info(f"Chunk {i + 1}:")
        logging.info(chunk)
        logging.info("-" * 50)  # Separator

    # Calculate total characters and estimate tokens
    total_chars = sum(len(chunk) for chunk in relevant_chunks)
    estimated_tokens = total_chars // 4  # Rough estimate: 1 token ≈ 4 characters

    logging.info(f"Total characters in retrieved chunks: {total_chars}")
    logging.info(f"Estimated tokens in retrieved chunks: {estimated_tokens}")

    # Join chunks and truncate if necessary
    context = " ".join(relevant_chunks)
    max_context_tokens = 800  # Adjust this value as needed
    if estimated_tokens > max_context_tokens:
        context = truncate_to_token_limit(context, max_context_tokens)
        logging.info(f"Context truncated to approximately {max_context_tokens} tokens")

    # Log the final context
    logging.info("Final context:")
    logging.info(context)
    logging.info("-" * 50)

    # Calculate and log token counts
    system_message = "You are an AI tutor helping to understand research papers. Use the following context to answer the user's question: "
    system_tokens = num_tokens_from_string(system_message)
    context_tokens = num_tokens_from_string(context)
    prompt_tokens = num_tokens_from_string(prompt)

    logging.info(f"System message tokens: {system_tokens}")
    logging.info(f"Context tokens: {context_tokens}")
    logging.info(f"Prompt tokens: {prompt_tokens}")
    logging.info(f"Total tokens: {system_tokens + context_tokens + prompt_tokens}")

    # Prepare messages
    messages = [
        {"role": "system", "content": system_message + context},
        {"role": "user", "content": prompt}
    ]

    # Display context in Streamlit (optional)
    with st.expander("View Retrieved Context"):
        st.text_area("Context", context, height=300)

    # Double-check total tokens
    total_tokens = sum(num_tokens_from_string(msg["content"]) for msg in messages)
    if total_tokens > 1000:
        st.warning(f"Total tokens ({total_tokens}) exceed 1000. The response may be truncated.")

    response = azure_client.get_completion(messages)
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    chat_history.add_message("assistant", response)

# Close the database connection
chat_history.close()