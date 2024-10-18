import streamlit as st
import os
from dotenv import load_dotenv
from azure_client import AzureClient
from pdf_processor import extract_text_from_pdf
from vector_db import VectorDB
from chat_history import ChatHistory
import tiktoken
import logging
import sys
import uuid

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Initialize components
azure_client = AzureClient(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    model_name=os.getenv("AZURE_OPENAI_MODEL_NAME")
)
vector_db = VectorDB()
chat_history = ChatHistory()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

# Sidebar for session management
st.sidebar.title("Chat Sessions")

# Function to create a new session
def create_new_session():
    session_id = str(uuid.uuid4())
    st.session_state.sessions[session_id] = []
    st.session_state.current_session_id = session_id
    st.session_state.messages = []

# Button to create a new session
if st.sidebar.button("New Chat"):
    create_new_session()

# Display existing sessions and allow switching
for session_id, session_messages in st.session_state.sessions.items():
    if st.sidebar.button(f"Session {session_id[:8]}", key=session_id):
        st.session_state.current_session_id = session_id
        st.session_state.messages = session_messages

# Add this after the session management buttons in the sidebar
if st.sidebar.button("Clear All Sessions"):
    st.session_state.sessions = {}
    st.session_state.messages = []
    st.session_state.current_session_id = None
    st.success("All sessions have been cleared.")

st.title("AI Research Paper Tutor")

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
if st.session_state.current_session_id:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to know about the research paper?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
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

        # Update the session
        st.session_state.sessions[st.session_state.current_session_id] = st.session_state.messages
else:
    st.info("Please create a new chat session or select an existing one from the sidebar.")

# Close the database connection
chat_history.close()