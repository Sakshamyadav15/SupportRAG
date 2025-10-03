"""
Streamlit frontend for SupportRAG.
Provides an interactive chat interface for querying the RAG system.
"""
import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional

# Page configuration
st.set_page_config(
    page_title="SupportRAG - AI Support Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_URL = "http://localhost:8000"
QUERY_ENDPOINT = f"{API_URL}/api/v1/query"
FAQ_ENDPOINT = f"{API_URL}/api/v1/faq"
METRICS_ENDPOINT = f"{API_URL}/api/v1/metrics"
HEALTH_ENDPOINT = f"{API_URL}/health"

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'metrics' not in st.session_state:
    st.session_state.metrics = {}


def check_api_health() -> bool:
    """Check if API is healthy."""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        return response.status_code == 200
    except:
        return False


def query_rag(question: str, top_k: int = 3) -> Optional[dict]:
    """Send query to RAG API."""
    try:
        payload = {
            "question": question,
            "top_k": top_k
        }
        response = requests.post(QUERY_ENDPOINT, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None


def get_metrics() -> Optional[dict]:
    """Fetch system metrics."""
    try:
        response = requests.get(METRICS_ENDPOINT, timeout=5)
        response.raise_for_status()
        return response.json()
    except:
        return None


def add_faq(question: str, answer: str, category: str = "general") -> bool:
    """Add a new FAQ."""
    try:
        payload = {
            "question": question,
            "answer": answer,
            "category": category
        }
        response = requests.post(FAQ_ENDPOINT, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except:
        return False


def format_citations(citations: list) -> str:
    """Format citations for display."""
    if not citations:
        return ""
    
    formatted = "### 📚 Sources\n\n"
    for i, citation in enumerate(citations, 1):
        formatted += f"**Source {i}** (Confidence: {citation['similarity_score']:.2%})\n"
        formatted += f"- **Q:** {citation['question']}\n"
        formatted += f"- **A:** {citation['answer']}\n\n"
    return formatted


# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    # API Health Check
    st.subheader("🔌 API Status")
    if check_api_health():
        st.success("✅ API Connected")
    else:
        st.error("❌ API Offline")
        st.info("Start the API with: `uvicorn src.api.main:app --reload`")
    
    st.divider()
    
    # Query settings
    st.subheader("🎛️ Query Settings")
    top_k = st.slider("Number of results", min_value=1, max_value=10, value=3)
    show_citations = st.checkbox("Show citations", value=True)
    
    st.divider()
    
    # Metrics
    st.subheader("📊 Metrics")
    if st.button("Refresh Metrics"):
        st.session_state.metrics = get_metrics()
    
    if st.session_state.metrics:
        metrics = st.session_state.metrics
        st.metric("Total Queries", metrics.get('total_queries', 0))
        st.metric("Avg Latency", f"{metrics.get('average_latency_ms', 0):.0f} ms")
        st.metric("Escalation Rate", f"{metrics.get('escalation_rate', 0):.1f}%")
        st.metric("Total FAQs", metrics.get('total_faqs', 0))
    
    st.divider()
    
    # Add FAQ Section
    with st.expander("➕ Add New FAQ"):
        with st.form("add_faq_form"):
            new_question = st.text_input("Question")
            new_answer = st.text_area("Answer")
            new_category = st.text_input("Category", value="general")
            
            if st.form_submit_button("Add FAQ"):
                if new_question and new_answer:
                    if add_faq(new_question, new_answer, new_category):
                        st.success("FAQ added successfully!")
                    else:
                        st.error("Failed to add FAQ")
                else:
                    st.warning("Please fill in both question and answer")

# Main content
st.title("🤖 SupportRAG - AI Support Assistant")
st.markdown("Ask me anything about our products and services!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show metadata for assistant messages
        if message["role"] == "assistant" and "metadata" in message:
            metadata = message["metadata"]
            
            # Show escalation warning
            if metadata.get("escalated"):
                st.warning("🚨 This query was escalated to a human agent")
            
            # Show confidence and latency
            col1, col2 = st.columns(2)
            with col1:
                confidence = metadata.get("confidence_score", 0)
                st.caption(f"Confidence: {confidence:.2%}")
            with col2:
                latency = metadata.get("latency_ms", 0)
                st.caption(f"Response time: {latency:.0f}ms")
            
            # Show citations
            if show_citations and "citations" in metadata and metadata["citations"]:
                with st.expander("📚 View Sources"):
                    for i, citation in enumerate(metadata["citations"], 1):
                        st.markdown(f"**Source {i}** (Relevance: {citation['similarity_score']:.2%})")
                        st.markdown(f"**Q:** {citation['question']}")
                        st.markdown(f"**A:** {citation['answer']}")
                        if i < len(metadata["citations"]):
                            st.divider()

# Chat input
if prompt := st.chat_input("Type your question here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = query_rag(prompt, top_k)
            
            if response:
                answer = response.get("answer", "I couldn't generate a response.")
                st.markdown(answer)
                
                # Show metadata
                metadata = {
                    "escalated": response.get("escalated", False),
                    "confidence_score": response.get("confidence_score", 0),
                    "latency_ms": response.get("latency_ms", 0),
                    "citations": response.get("citations", [])
                }
                
                # Show escalation warning
                if metadata["escalated"]:
                    st.warning("🚨 This query was escalated to a human agent")
                
                # Show confidence and latency
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"Confidence: {metadata['confidence_score']:.2%}")
                with col2:
                    st.caption(f"Response time: {metadata['latency_ms']:.0f}ms")
                
                # Show citations
                if show_citations and metadata["citations"]:
                    with st.expander("📚 View Sources"):
                        for i, citation in enumerate(metadata["citations"], 1):
                            st.markdown(f"**Source {i}** (Relevance: {citation['similarity_score']:.2%})")
                            st.markdown(f"**Q:** {citation['question']}")
                            st.markdown(f"**A:** {citation['answer']}")
                            if i < len(metadata["citations"]):
                                st.divider()
                
                # Add to session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "metadata": metadata
                })
            else:
                error_msg = "Failed to get response from API. Please check if the API is running."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center'>
        <p>Powered by SupportRAG | Built with FastAPI, LangChain & Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Clear chat button
if st.session_state.messages:
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
