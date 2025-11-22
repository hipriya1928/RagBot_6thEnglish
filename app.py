import streamlit as st
from rag_bot import RAGBot
import os

# Page Config
st.set_page_config(page_title="Class 6 English RAG Bot", page_icon="📚", layout="wide")

# Title and Description
st.title("📚 TN Class 6 English RAG Bot")
st.markdown("""
This bot answers questions from the **Tamil Nadu State Board Class 6 English Textbook**.
It uses **ChromaDB** for text search and **Neo4j** for knowledge graph relationships.
""")

# Initialize Bot
@st.cache_resource
def get_bot():
    try:
        return RAGBot()
    except Exception as e:
        st.error(f"Failed to initialize bot: {e}")
        return None

bot = get_bot()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask a question about the stories..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    if bot:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response, context = bot.generate_response(prompt)
                    st.markdown(response)
                    
                    # Add assistant message to history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Show Context in Expander
                    with st.expander("View Retrieval Context (Debug)"):
                        st.text(context)
                        
                except Exception as e:
                    st.error(f"Error generating response: {e}")
    else:
        st.error("Bot is not initialized. Please check your .env configuration.")

# Sidebar
with st.sidebar:
    st.header("About")
    st.info("This system combines Vector Search (Semantic) and Graph Search (Structured) to reduce hallucinations.")
    
    st.subheader("Tech Stack")
    st.code("LangChain\nChromaDB\nNeo4j\nOpenAI GPT-4o")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
