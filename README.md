---
title: RAG Document Chatbot
emoji: books
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# RAG Document Chatbot

A Retrieval-Augmented Generation chatbot that answers questions about PDFs
with inline citations to source pages.

Built framework-free - every part of the RAG pipeline is explicit and readable.

## Architecture

User query -> fastembed vector -> cosine similarity over chunk matrix
-> top-k chunks -> prompt with context -> Groq (gpt-oss-120b) -> answer + [n] citations

## Features

- Grounded answers only - refuses when the answer is not in the documents
- Inline citations - each claim points to a [n] source with page number
- Multi-turn - remembers conversation context
- Portable - runs locally, on HF Spaces, or on Render
- Small footprint - fastembed ONNX model (~50MB), no GPU

## Run locally

    pip install -r requirements.txt
    export GROQ_API_KEY=gsk_...
    chainlit run app.py -h

Open http://localhost:8000.

## Run with Docker

    docker build -t rag-chatbot .
    docker run -e GROQ_API_KEY=gsk_... -p 7860:7860 rag-chatbot

Open http://localhost:7860.

## Project structure

    app.py            Chainlit UI
    rag_core.py       pipeline (retrieval + prompting)
    requirements.txt
    Dockerfile
    pdfs/             source PDFs
    README.md

## Configuration

- GROQ_API_KEY (required) - Groq API key
- EMBED_MODEL_NAME (default: BAAI/bge-small-en-v1.5)

Tuning in rag_core.py:
- CHUNK_WORDS = 200
- OVERLAP_WORDS = 40
- k=4 in ask()

## Design decisions

- fastembed (ONNX) over sentence-transformers: no torch, no transformers
- numpy cosine similarity over a vector DB: fast for <10k chunks
- Dynamic model selection: queries Groq /models at startup
- Reasoning-aware retry: handles gpt-oss token budget
- Citation cleanup: strips odd bracket artifacts

## License

MIT
