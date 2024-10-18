# AI Research Paper Tutor

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

## Overview

This AI Research Paper Tutor is a Streamlit application that uses Azure OpenAI to help users understand research papers. It leverages a vector database to store and retrieve relevant context from papers, providing intelligent responses to user queries.

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.8 or higher
- An Azure account with access to Azure OpenAI
- Azure OpenAI API key and endpoint

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/shenron54/ai-tutor.git
   cd ai-research-paper-tutor
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the root directory of the project.

2. Add your Azure OpenAI credentials to the `.env` file:
   ```
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=your_endpoint_here
   AZURE_OPENAI_MODEL_NAME=your_model_name_here
   ```

## Running the Application

To run the Streamlit application:

```
streamlit run app.py
```

The application should now be accessible at `http://localhost:8501`.

## Usage

1. **Upload a Paper**: Use the file uploader to add a research paper to the vector database.

2. **Ask Questions**: Type your question about the paper in the text input field.

3. **View Results**: The AI will provide an answer based on the context from the uploaded papers.

4. **Explore Context**: Expand the "View Retrieved Context" section to see what information was used to generate the response.

## Troubleshooting

### Rate Limit Errors

If you encounter rate limit errors:

1. Check the logs in the terminal for token usage information.
2. Adjust the `max_context_tokens` variable in `app.py` to reduce the context size.
3. Modify the `max_chunk_size` in the `VectorDB` class to control the size of stored chunks.

### Other Issues

- Ensure all environment variables are correctly set in the `.env` file.
- Verify that your Azure OpenAI subscription is active and has available quota.
- Check the Streamlit and application logs for any error messages.

If problems persist, please open an issue on the GitHub repository with detailed information about the error and steps to reproduce it.
```