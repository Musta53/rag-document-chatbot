"""rag_core.py - Framework-free RAG pipeline."""
import os, re
from pathlib import Path
import numpy as np
from pypdf import PdfReader
from fastembed import TextEmbedding
from groq import Groq

EMBED_MODEL_NAME = os.environ.get("EMBED_MODEL_NAME", "BAAI/bge-tiny-en-v1.5")
CHUNK_WORDS, OVERLAP_WORDS = 200, 40
PREFERRED_MODELS = [
    "openai/gpt-oss-120b", "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile", "llama-3.1-8b-instant",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "qwen/qwen3-32b", "moonshotai/kimi-k2-instruct",
]
SYSTEM_PROMPT = """You are a precise document Q&A assistant.

RULES:
1. Answer ONLY using the CONTEXT blocks provided.
2. If the context does not contain the answer, say exactly:
   "I couldn't find that in the provided documents."
3. Cite every claim with numeric markers like [1], [2].
4. NEVER use any other citation format.
5. Be concise. 2-4 sentences unless the user asks for detail.
"""

def pick_model(client):
    avail = {m.id for m in client.models.list().data}
    for m in PREFERRED_MODELS:
        if m in avail:
            return m
    for m in sorted(avail):
        if any(k in m.lower() for k in ("instruct","chat","oss","llama","qwen","kimi")):
            return m
    raise RuntimeError(f"No chat model. Available: {sorted(avail)}")

def extract_pages(pdf_path):
    reader = PdfReader(str(pdf_path))
    src = os.path.basename(str(pdf_path))
    out = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            out.append({"text": text, "page": i, "source": src})
    return out

def chunk_text(text, chunk_words=CHUNK_WORDS, overlap=OVERLAP_WORDS):
    words = text.split()
    if len(words) <= chunk_words:
        return [" ".join(words)]
    chunks, step = [], chunk_words - overlap
    for i in range(0, len(words), step):
        c = words[i:i + chunk_words]
        if c:
            chunks.append(" ".join(c))
        if i + chunk_words >= len(words):
            break
    return chunks

def clean_citations(text):
    text = re.sub(r"\u3010[^\u3011]*\u3011", "", text)
    text = re.sub(r"\(Source \d+\)", "", text)
    return re.sub(r"\s+", " ", text).strip()

class RAGPipeline:
    def __init__(self, pdf_dir="pdfs", groq_api_key=None):
        self.pdf_dir = Path(pdf_dir)
        self.embedder = TextEmbedding(model_name=EMBED_MODEL_NAME)
        api_key = groq_api_key or os.environ["GROQ_API_KEY"]
        self.client = Groq(api_key=api_key)
        self.model = pick_model(self.client)
        self.chunks = []
        self.embeddings_norm = None

    def build_index(self):
        pdfs = sorted(self.pdf_dir.glob("*.pdf"))
        if not pdfs:
            raise RuntimeError(f"No PDFs in {self.pdf_dir}")
        all_pages = []
        for pdf in pdfs:
            all_pages.extend(extract_pages(pdf))
        self.chunks = []
        for page in all_pages:
            for j, ctext in enumerate(chunk_text(page["text"])):
                self.chunks.append({
                    "text": ctext, "source": page["source"],
                    "page": page["page"],
                    "chunk_id": f"{page['source']}#p{page['page']}#c{j}",
                })
        vecs = np.array([e.tolist() for e in
                         self.embedder.embed([c["text"] for c in self.chunks])])
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.embeddings_norm = vecs / norms
        return len(self.chunks)

    def retrieve(self, query, k=4):
        qvec = np.array(next(self.embedder.embed([query])).tolist())
        qvec = qvec / (np.linalg.norm(qvec) or 1.0)
        scores = self.embeddings_norm @ qvec
        top_k = np.argsort(scores)[::-1][:k]
        return [{**self.chunks[i], "score": float(scores[i])} for i in top_k]

    def ask(self, question, history=None, k=4, temperature=0.1, max_tokens=800):
        hits = self.retrieve(question, k=k)
        ctx = "\n\n".join(
            f"[{i}] (source: {h['source']}, page {h['page']})\n{h['text']}"
            for i, h in enumerate(hits, start=1))
        user_msg = (f"CONTEXT:\n{ctx}\n\nQUESTION: {question}\n\n"
                    f"Answer using the context above and cite sources with [n].")
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_msg})
        resp = self.client.chat.completions.create(
            model=self.model, messages=messages,
            temperature=temperature, max_tokens=max_tokens)
        choice = resp.choices[0]
        answer = (choice.message.content or "").strip()
        if not answer and choice.finish_reason == "length":
            resp = self.client.chat.completions.create(
                model=self.model, messages=messages,
                temperature=temperature, max_tokens=max_tokens,
                reasoning_effort="low")
            answer = (resp.choices[0].message.content or "").strip()
        answer = clean_citations(answer) or "(No answer returned.)"
        sources = [{"n": i, "source": h["source"], "page": h["page"],
                    "chunk_id": h["chunk_id"], "score": h["score"]}
                   for i, h in enumerate(hits, start=1)]
        return {"answer": answer, "sources": sources, "model": self.model}
