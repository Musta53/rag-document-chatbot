import streamlit as st
from utils.rag_pipeline import load_pdf_text, ask_question

st.set_page_config(page_title="Simple RAG Chatbot", page_icon="📄")

st.title("📄 Simple RAG Document Chatbot")
st.write("This version is lighter and more compatible with your system.")

# Load document text
if "context" not in st.session_state:
    with st.spinner("Loading documents..."):
        st.session_state.context = load_pdf_text()
        st.success("Documents loaded!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = ask_question(prompt, st.session_state.context)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error: {e}")
