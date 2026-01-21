"""Streamlit Chatbot UI for Jarvis AI Assistant"""

import streamlit as st
import requests
from typing import Optional

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Jarvis AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def check_api_status() -> Optional[dict]:
    """Check if the API is running and get status"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/status", timeout=5)
        response.raise_for_status()
        return response.json()
    except:
        return None


def send_message(message: str, use_knowledge_base: bool = True) -> Optional[dict]:
    """Send a message to the API and get response"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json={"message": message, "use_knowledge_base": use_knowledge_base},
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def add_knowledge(documents: list) -> bool:
    """Add documents to knowledge base"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/knowledge/add",
            json={"documents": documents},
            timeout=30
        )
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error adding knowledge: {str(e)}")
        return False


def get_knowledge() -> Optional[dict]:
    """Get all knowledge from database"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/knowledge", timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return None


def clear_knowledge() -> bool:
    """Clear all knowledge from database"""
    try:
        response = requests.delete(f"{API_BASE_URL}/api/knowledge", timeout=10)
        response.raise_for_status()
        return True
    except:
        return False


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "knowledge_count" not in st.session_state:
    st.session_state.knowledge_count = 0


# Main UI
st.title("🤖 Jarvis AI Assistant")
st.markdown("*Your Personal AI Assistant powered by LLaMA & ChromaDB*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings & Status")

    # Check API Status
    status = check_api_status()

    if status:
        st.success("✅ API Connected")

        # Ollama Status
        if status.get("ollama_running"):
            st.success("✅ Ollama Running")
            if status.get("model_available"):
                st.success(f"✅ Model: {status.get('selected_model')}")
            else:
                st.warning(f"⚠️ Model '{status.get('selected_model')}' not found")
                st.info("Run: `ollama pull llama2`")
        else:
            st.error("❌ Ollama Not Running")
            st.info("Run: `ollama serve`")

        # Knowledge Base Stats
        st.markdown("---")
        st.subheader("📚 Knowledge Base")
        st.metric("Documents", status.get("knowledge_base_count", 0))
        st.session_state.knowledge_count = status.get("knowledge_base_count", 0)
    else:
        st.error("❌ API Not Connected")
        st.info("Start the API with:\n`uvicorn app.main:app --reload`")

    # Settings
    st.markdown("---")
    st.subheader("🎛️ Chat Settings")
    use_kb = st.checkbox("Use Knowledge Base", value=True, help="Include context from knowledge base in responses")

    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


# Main content area with tabs
tab1, tab2 = st.tabs(["💬 Chat", "📚 Knowledge Base"])

# Chat Tab
with tab1:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("context_used"):
                with st.expander("📄 Context Used"):
                    for doc in message.get("retrieved_docs", []):
                        st.markdown(f"- {doc.get('document', '')[:200]}...")

    # Chat input
    if prompt := st.chat_input("Ask Jarvis anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_message(prompt, use_kb)

                if response:
                    assistant_message = response.get("response", "Sorry, I couldn't generate a response.")
                    st.markdown(assistant_message)

                    # Show context if used
                    if response.get("context_used") and response.get("retrieved_documents"):
                        with st.expander("📄 Context Used"):
                            for doc in response.get("retrieved_documents", []):
                                st.markdown(f"- {doc.get('document', '')[:200]}...")

                    # Save to session state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_message,
                        "context_used": response.get("context_used", False),
                        "retrieved_docs": response.get("retrieved_documents", [])
                    })
                else:
                    error_msg = "Failed to get response. Please check if the API and Ollama are running."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

# Knowledge Base Tab
with tab2:
    st.subheader("📚 Manage Knowledge Base")
    st.markdown("Add information that Jarvis can use to answer your questions.")

    # Add knowledge
    with st.form("add_knowledge_form"):
        st.markdown("### Add New Knowledge")
        new_knowledge = st.text_area(
            "Enter information to add:",
            height=150,
            placeholder="Enter facts, documentation, or any information you want Jarvis to know..."
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            submit_btn = st.form_submit_button("➕ Add Knowledge")

        if submit_btn and new_knowledge.strip():
            with st.spinner("Adding to knowledge base..."):
                # Split by double newlines for multiple documents
                docs = [d.strip() for d in new_knowledge.split("\n\n") if d.strip()]
                if add_knowledge(docs):
                    st.success(f"Successfully added {len(docs)} document(s)!")
                    st.rerun()

    st.markdown("---")

    # View current knowledge
    st.markdown("### Current Knowledge")
    knowledge = get_knowledge()

    if knowledge and knowledge.get("count", 0) > 0:
        st.info(f"📊 Total documents: {knowledge.get('count', 0)}")

        docs = knowledge.get("documents", {})
        if docs.get("documents"):
            for i, (doc_id, doc_text) in enumerate(zip(docs.get("ids", []), docs.get("documents", []))):
                with st.expander(f"Document {i+1}: {doc_text[:50]}..."):
                    st.markdown(doc_text)
                    st.caption(f"ID: {doc_id}")

        # Clear knowledge base
        st.markdown("---")
        if st.button("🗑️ Clear All Knowledge", type="secondary"):
            if clear_knowledge():
                st.success("Knowledge base cleared!")
                st.rerun()
    else:
        st.info("No documents in knowledge base yet. Add some knowledge above!")

    # Sample knowledge suggestions
    st.markdown("---")
    st.markdown("### 💡 Quick Add Examples")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Add Sample: Company Info"):
            sample = """Our company, TechCorp, was founded in 2020.
We specialize in AI solutions and have offices in San Francisco and New York.
Our CEO is Jane Smith and we have over 500 employees."""
            if add_knowledge([sample]):
                st.success("Added sample company info!")
                st.rerun()

    with col2:
        if st.button("Add Sample: Product Info"):
            sample = """Our main product is JarvisAI, an enterprise AI assistant.
It features natural language processing, knowledge management, and integrations with popular tools.
Pricing starts at $99/month for small teams."""
            if add_knowledge([sample]):
                st.success("Added sample product info!")
                st.rerun()


# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Built with ❤️ using LLaMA, ChromaDB, FastAPI & Streamlit"
    "</div>",
    unsafe_allow_html=True
)
