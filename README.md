# Resume Agent

HR chatbot that lets you chat with candidates' resumes using RAG.

## Prerequisites

- Docker

## Setup

1. Clone the repo and enter the directory.

2. Copy `.env` and add your OpenRouter API key:

```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

Get a key at https://openrouter.ai/keys.

3. Build and run:

```
docker compose up --build
```

4. Open http://localhost:8501 in your browser.

## Usage

1. Upload one or more resumes (PDF, DOCX, or TXT) via the sidebar.
2. Click **Process Resumes** to index them.
3. Ask questions about candidates in the chat input.

## Architecture

```
Streamlit UI → FastAPI → LangChain RAG
                        ├── PyMuPDF / python-docx (parse)
                        ├── OpenRouter embeddings
                        ├── ChromaDB (vector store)
                        └── OpenRouter LLM (free models)
```

## Stopping

```
docker compose down
```
