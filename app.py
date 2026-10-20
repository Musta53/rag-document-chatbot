import streamlit as st
from utils.rag_pipeline import load_pdf_text, ask_question

st.set_page_config(
    page_title="RAG Document Chatbot",
    page_icon="📄",
    layout="centered"
)

# Custom CSS for green border and button
st.markdown("""
<style>
    /* Chat input border - green and thicker */
    div[data-testid="stChatInput"] textarea {
        border: 2.5px solid #28a745 !important;
        border-radius: 12px !important;
    }

    /* Send button - green */
    div[data-testid="stChatInput"] button {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }

    div[data-testid="stChatInput"] button:hover {
        background-color: #218838 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 RAG Document Chatbot")

# Load documents only once
if "context" not in st.session_state:
    st.session_state.context = load_pdf_text()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
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
