# Custom CSS for better look
st.markdown("""
<style>
    /* Make the chat input border green and thicker */
    div[data-testid="stChatInput"] textarea {
        border: 2.5px solid #28a745 !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }

    /* Change the send button to green */
    div[data-testid="stChatInput"] button {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }

    div[data-testid="stChatInput"] button:hover {
        background-color: #218838 !important;
        color: white !important;
    }

    /* Also target the form submit button just in case */
    button[kind="primary"] {
        background-color: #28a745 !important;
        border-color: #28a745 !important;
    }
</style>
""", unsafe_allow_html=True)
