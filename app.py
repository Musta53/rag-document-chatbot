"""Chainlit UI for the RAG Document Chatbot."""
import os
import chainlit as cl
from rag_core import RAGPipeline, EMBED_MODEL_NAME

_pipeline = None

def get_pipeline():
    global _pipeline
    if _pipeline is None:
        p = RAGPipeline(pdf_dir="pdfs")
        n = p.build_index()
        print(f"[startup] Indexed {n} chunks, model={p.model}")
        _pipeline = p
    return _pipeline

@cl.on_chat_start
async def on_chat_start():
    p = get_pipeline()
    cl.user_session.set("history", [])
    await cl.Message(content=(
        f"**RAG Document Chatbot ready**\n\n"
        f"Model: `{p.model}` | Embeddings: `{EMBED_MODEL_NAME}` | "
        f"Indexed chunks: **{len(p.chunks)}**\n\n"
        f"Ask anything about the bundled PDFs. Sources appear under each answer."
    )).send()

@cl.on_message
async def on_message(message: cl.Message):
    p = get_pipeline()
    history = cl.user_session.get("history") or []
    async with cl.Step(name="Retrieving + answering", type="tool") as step:
        step.input = message.content
        result = p.ask(message.content, history=history)
    history.append({"role": "user", "content": message.content})
    history.append({"role": "assistant", "content": result["answer"]})
    cl.user_session.set("history", history)
    src_lines = "\n".join(
        f"- **[{s['n']}]** `{s['source']}` p.{s['page']} | score {s['score']:.3f}"
        for s in result["sources"])
    await cl.Message(content=f"{result['answer']}\n\n---\n**Sources**\n{src_lines}").send()
