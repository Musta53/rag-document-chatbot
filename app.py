import streamlit as st
from utils.rag_pipeline import load_pdf_text, ask_question

st.set_page_config(
    page_title="RAG Document Chatbot",
    page_icon="📄",
    layout="centered"
)

# Stronger Custom CSS
st.markdown("""
<style>
    /* Main chat input container */
    div[data-testid="stChatInput"] {
        border: 2.5px solid #28a745 !important;
        border-radius: 14px !important;
        padding: 4px !important;
        background-color: white !important;
        max-width: 720px !important;
        margin: 0 auto !important;
        box-shadow: none !important;
    }

    /* Remove any red outline */
    div[data-testid="stChatInput"]:focus-within {
        border-color: #28a745 !important;
        box-shadow: 0 0 0 1px #28a745 !important;
    }

    /* Textarea inside */
    div[data-testid="stChatInput"] textarea {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
        padding: 12px 55px 12px 16px !important;
        font-size: 16px !important;
        min-height: 52px !important;
    }

    /* Send button */
    div[data-testid="stChatInput"] button {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        width: 40px !important;
        height: 40px !important;
        margin: 6px 8px 6px 0 !important;
    }

    div[data-testid="stChatInput"] button:hover {
        background-color: #218838 !important;
    }

    /* Hide placeholder artifacts / dots */
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #999 !important;
        opacity: 0.7 !important;
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
