"""
Enhanced Streamlit UI for Dual Vector Store RAG
Shows source (FAQ vs Ticket), resolution status, and categories
"""
import streamlit as st
import requests
from datetime import datetime
from typing import Dict, Any

# Configure page
st.set_page_config(
    page_title="SupportRAG Enhanced",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .source-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 600;
        margin: 4px 0;
    }
    .source-faq {
        background-color: #e3f2fd;
        color: #1976d2;
    }
    .source-ticket {
        background-color: #fff3e0;
        color: #f57c00;
    }
    .status-open {
        background-color: #ffebee;
        color: #c62828;
    }
    .status-closed {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    .citation-card {
        background-color: #f5f5f5;
        border-left: 4px solid #2196f3;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
    }
    .confidence-high { color: #2e7d32; font-weight: bold; }
    .confidence-medium { color: #f57c00; font-weight: bold; }
    .confidence-low { color: #c62828; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


def check_api_health() -> bool:
    """Check if API is healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def query_rag(question: str, top_k: int = 3) -> Dict[str, Any]:
    """Query the RAG API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": question, "top_k": top_k},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error querying API: {e}")
        return None


def trigger_ingestion(rebuild: bool = False) -> Dict[str, Any]:
    """Trigger data ingestion"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/ingest",
            json={"rebuild": rebuild},
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error triggering ingestion: {e}")
        return None


def get_stats() -> Dict[str, Any]:
    """Get system statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        response.raise_for_status()
        return response.json()
    except:
        return None


def format_confidence(confidence: float) -> str:
    """Format confidence with color coding"""
    pct = confidence * 100
    if pct >= 70:
        css_class = "confidence-high"
        emoji = "✅"
    elif pct >= 50:
        css_class = "confidence-medium"
        emoji = "⚠️"
    else:
        css_class = "confidence-low"
        emoji = "❌"
    
    return f'{emoji} <span class="{css_class}">{pct:.1f}%</span>'


def display_citation(citation: Dict[str, Any], index: int):
    """Display a single citation"""
    source = citation['source']
    category = citation.get('category', 'General')
    similarity = citation['similarity'] * 100
    
    # Source badge
    source_class = "source-faq" if source == "FAQ" else "source-ticket"
    
    html = f"""
    <div class="citation-card">
        <div>
            <span class="source-badge {source_class}">{source}</span>
            <span class="source-badge" style="background-color: #f5f5f5; color: #666;">
                {category}
            </span>
            <span style="float: right; color: #666; font-size: 0.9em;">
                Match: {similarity:.1f}%
            </span>
        </div>
    """
    
    # Add resolution status for tickets
    if source == "Ticket" and 'resolution_status' in citation:
        status = citation['resolution_status']
        status_class = "status-closed" if status == "closed" else "status-open"
        html += f'<div style="margin-top: 8px;"><span class="source-badge {status_class}">Status: {status.upper()}</span></div>'
    
    html += f"""
        <div style="margin-top: 8px; color: #444; font-size: 0.9em;">
            {citation['content']}
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


# Main App
def main():
    st.title("🤖 SupportRAG Enhanced")
    st.markdown("*AI-Powered Customer Support with Dual Vector Stores*")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Control")
        
        # API Health
        if check_api_health():
            st.success("✅ API Connected")
        else:
            st.error("❌ API Offline")
            st.info("Start the API: `python -m src.api.main_enhanced`")
            return
        
        st.divider()
        
        # Ingestion Controls
        st.subheader("📥 Data Ingestion")
        
        if st.button("🔄 Build Vector Stores", use_container_width=True):
            with st.spinner("Building vector stores..."):
                result = trigger_ingestion(rebuild=True)
                if result:
                    st.success(result['message'])
                    st.info(f"FAQ: {result['faq_count']} | Tickets: {result['ticket_count']}")
        
        if st.button("📂 Load Existing Stores", use_container_width=True):
            with st.spinner("Loading vector stores..."):
                result = trigger_ingestion(rebuild=False)
                if result:
                    st.success(result['message'])
        
        st.divider()
        
        # Statistics
        st.subheader("📊 Statistics")
        stats = get_stats()
        if stats and stats['total_queries'] > 0:
            st.metric("Total Queries", stats['total_queries'])
            st.metric("Avg Latency", f"{stats['avg_latency_ms']:.0f}ms")
            st.metric("Avg Confidence", f"{stats['avg_confidence']*100:.1f}%")
            
            if stats['source_breakdown']:
                st.write("**Source Breakdown:**")
                for source, count in stats['source_breakdown'].items():
                    pct = (count / stats['total_queries']) * 100
                    st.write(f"- {source}: {count} ({pct:.1f}%)")
        else:
            st.info("No queries yet")
        
        st.divider()
        
        # Settings
        st.subheader("🎛️ Settings")
        top_k = st.slider("Results per query", 1, 10, 3)
    
    # Main Chat Interface
    st.header("💬 Ask a Question")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display metadata for assistant messages
            if message["role"] == "assistant" and "metadata" in message:
                metadata = message["metadata"]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Source:** {metadata['source']}")
                with col2:
                    st.markdown(f"**Confidence:** {format_confidence(metadata['confidence'])}", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"**Latency:** {metadata['latency_ms']:.0f}ms")
                
                # Show citations
                if metadata.get('citations'):
                    with st.expander(f"📚 View {len(metadata['citations'])} Sources"):
                        for i, citation in enumerate(metadata['citations']):
                            display_citation(citation, i)
    
    # Chat input
    if prompt := st.chat_input("Ask about orders, refunds, account issues..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Query RAG
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = query_rag(prompt, top_k=top_k)
            
            if result:
                # Display answer
                st.markdown(result['answer'])
                
                # Display metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    source = result['source']
                    source_class = "source-faq" if source == "FAQ" else "source-ticket"
                    st.markdown(f'<span class="source-badge {source_class}">{source}</span>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f"**Confidence:** {format_confidence(result['confidence'])}", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"**Latency:** {result['latency_ms']:.0f}ms")
                
                # Show citations
                if result.get('citations'):
                    with st.expander(f"📚 View {len(result['citations'])} Sources"):
                        for i, citation in enumerate(result['citations']):
                            display_citation(citation, i)
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result['answer'],
                    "metadata": result
                })
            else:
                st.error("Failed to get response from API")
    
    # Example questions
    st.divider()
    st.subheader("💡 Try These Examples")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 How do I track my order?", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "How do I track my order?"})
            st.rerun()
        
        if st.button("💰 My refund hasn't arrived", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "My refund hasn't arrived in 12 days"})
            st.rerun()
    
    with col2:
        if st.button("🔑 Can't log into my account", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "I can't log into my account even after resetting password"})
            st.rerun()
        
        if st.button("📦 Product arrived damaged", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "The product I received is damaged"})
            st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", type="secondary"):
        st.session_state.messages = []
        st.rerun()


if __name__ == "__main__":
    main()
