FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Warm the fastembed cache so first user request is fast
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='BAAI/bge-tiny-en-v1.5')" || true

# Render provides $PORT; HF Spaces needs 7860 — handle both
ENV PORT=7860
EXPOSE 7860

CMD chainlit run app.py --host 0.0.0.0 --port ${PORT} -h
