import os
from openai import OpenAI
from pypdf import PdfReader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Please check your .env file.")

client = OpenAI(api_key=api_key)


def load_pdf_text(data_path="data"):
    """Load text from all PDFs in the data folder"""
    all_text = ""
    for filename in os.listdir(data_path):
        if filename.endswith(".pdf"):
            filepath = os.path.join(data_path, filename)
            reader = PdfReader(filepath)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"
    return all_text


def ask_question(question, context):
    """Ask the LLM a question based on the document context"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer the question based only on the provided context. If you don't know the answer, say you don't know."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ],
        temperature=0.2
    )
    return response.choices[0].message.content
