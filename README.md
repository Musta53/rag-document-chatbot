# Simple RAG Document Chatbot

A simple Retrieval-Augmented Generation (RAG) chatbot that allows you to ask questions about your own PDF documents.

This project uses OpenAI's GPT model to answer questions based on the content of uploaded PDFs.

## Features

- Upload PDF documents
- Ask questions about the documents
- Get answers based only on the document content
- Simple and lightweight (compatible with more systems)

## How it Works

1. The system reads the PDF files from the `data` folder
2. It extracts the text from the documents
3. When you ask a question, it sends the document content + your question to OpenAI
4. The AI answers based on the documents

## Project Structure


rag-document-chatbot/
├── app.py                 # Main Streamlit application
├── utils/
│   └── rag_pipeline.py    # Core logic for loading documents and asking questions
├── data/                  # Put your PDF files here
├── .env                   # Your OpenAI API key (not uploaded to GitHub)
├── requirements.txt
└── README.md



## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate


Install the required packages:Bash


pip install -r requirements.txt


Create a .env file and add your OpenAI API key


OPENAI_API_KEY=your_openai_api_key_here



Put your PDF files inside the data folder
Run the application


streamlit run app.py


Requirements

Python 3.9+
OpenAI API key (with available credits)



Note
This is a simplified version of a RAG system for better compatibility.

A more advanced version using LangChain and vector databases can be built later


