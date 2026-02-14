"""
Enterprise LLMOps RAG Frontend

A comprehensive Streamlit interface for Retrieval-Augmented Generation with:
- Document upload and management
- Real-time RAG question answering
- Document search and retrieval
- Statistics and monitoring
- Production and demo modes
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
from typing import List, Dict, Any
import time
import os

# Page configuration
st.set_page_config(
    page_title="Enterprise LLMOps RAG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .metric-box {
        background: linear-gradient(135deg, #FFD89B 0%, #FFA500 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 6px solid #FF8C00;
        border: 2px solid #FF8C00;
        box-shadow: 0 4px 12px rgba(255, 140, 0, 0.3);
        color: #333;
        font-weight: 600;
    }
    .success-box {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        padding: 25px;
        border-radius: 10px;
        border-left: 6px solid #2E7D32;
        border: 2px solid #2E7D32;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
        color: white;
        font-size: 16px;
        line-height: 1.6;
    }
    .error-box {
        background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 6px solid #c41c3b;
        border: 2px solid #c41c3b;
        box-shadow: 0 4px 12px rgba(244, 67, 54, 0.3);
        color: white;
        font-weight: 600;
    }
    .response-header {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .info-label {
        color: #FF8C00;
        font-weight: bold;
        font-size: 14px;
        margin-top: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if "mode" not in st.session_state:
    st.session_state.mode = "Production"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "docs_uploaded" not in st.session_state:
    st.session_state.docs_uploaded = 0

# API Configuration
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
DEMO_MODE = False  # Set to True for demo mode

def call_api(endpoint: str, method: str = "GET", json_data: Dict = None, files: Dict = None):
    """Make API calls with error handling."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            resp = requests.get(url, timeout=30)
        elif method == "POST":
            if files:
                resp = requests.post(url, data=json_data, files=files, timeout=60)
            else:
                resp = requests.post(url, json=json_data, timeout=30)
        
        if resp.status_code == 200:
            return resp.json(), None
        else:
            return None, f"Error {resp.status_code}: {resp.text}"
    except requests.exceptions.ConnectionError:
        return None, "⚠️ API server not running. Make sure to start: uvicorn api_gateway.main:app --reload"
    except requests.exceptions.Timeout:
        return None, "⚠️ API request timeout"
    except Exception as e:
        return None, f"Error: {str(e)}"


# Sidebar Navigation
st.sidebar.markdown("### 📊 Enterprise LLMOps RAG")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📤 Upload Documents", "❓ Ask Questions", "🔍 Search", "📈 Analytics", "⚙️ Settings"]
)

st.sidebar.divider()

# System Status
with st.sidebar:
    st.markdown("### System Status")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Status"):
            data, error = call_api("/health")
            if data:
                st.success("✓ API Online")
            else:
                st.error("✗ API Offline")
    
    with col2:
        if st.button("📊 Stats"):
            data, error = call_api("/stats")
            if data:
                st.session_state.stats = data
                st.info(f"Docs: {data.get('vector_store', {}).get('total_vectors', 0)}")


# HOME PAGE
if page == "🏠 Home":
    st.markdown("""
    <div class="header">
        <h1>🤖 Enterprise LLMOps RAG System</h1>
        <p>Production-Ready Retrieval-Augmented Generation with Document Management</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📄 Document Management**
        - Upload PDFs, Word, Text
        - Automatic chunking
        - Vector embedding
        - Persistent storage
        """)
    
    with col2:
        st.markdown("""
        **❓ Smart Q&A**
        - Real-time retrieval
        - Context-aware answers
        - Multi-document synthesis
        - Question rephrasing
        """)
    
    with col3:
        st.markdown("""
        **📊 Enterprise Features**
        - Usage analytics
        - Document indexing
        - Search capabilities
        - Performance monitoring
        """)
    
    st.divider()
    
    # Quick Stats
    st.markdown("### System Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    data, _ = call_api("/stats")
    
    if data:
        stats = data.get("vector_store", {})
        with col1:
            st.metric("📚 Documents Indexed", stats.get("total_vectors", 0))
        with col2:
            st.metric("🔍 Embedding Dimension", stats.get("embedding_dimension", 1536))
        with col3:
            st.metric("💾 Index Type", stats.get("index_type", "Unknown"))
        with col4:
            st.metric("⏰ Current Time", datetime.now().strftime("%H:%M:%S"))
    
    st.divider()
    
    # Getting Started
    st.markdown("### 🚀 Getting Started")
    st.markdown("""
    1. **Upload Documents** - Go to "Upload Documents" tab to add PDFs or text files
    2. **Ask Questions** - Ask questions in the "Ask Questions" tab
    3. **Get Answers** - System retrieves relevant documents and generates answers
    4. **Monitor Usage** - View analytics and performance metrics
    """)


# UPLOAD DOCUMENTS PAGE
elif page == "📤 Upload Documents":
    st.title("📤 Upload & Index Documents")
    
    st.markdown("Upload documents to build your knowledge base. Supported formats: PDF, TXT, DOCX")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Choose files",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True,
            help="Upload documents to index them into the vector database"
        )
    
    with col2:
        st.markdown("### File Info")
        if uploaded_files:
            st.info(f"Files selected: {len(uploaded_files)}")
    
    if uploaded_files:
        st.divider()
        
        # Process files
        if st.button("📥 Index Documents", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Prepare files for upload
                files_to_upload = []
                for file in uploaded_files:
                    files_to_upload.append(("files", (file.name, file.getvalue(), file.type)))
                
                status_text.text("Uploading and indexing documents...")
                
                # Call upload endpoint
                response = requests.post(
                    f"{API_BASE_URL}/upload_documents",
                    files=[("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files],
                    timeout=60
                )
                
                progress_bar.progress(0.5)
                
                if response.status_code == 200:
                    data = response.json()
                    progress_bar.progress(1.0)
                    
                    st.success(f"""
                    ✓ Successfully indexed documents!
                    
                    📊 Results:
                    - Files Processed: {data.get('files_processed', 0)}
                    - Document Chunks: {data.get('chunks_created', 0)}
                    - Message: {data.get('message', 'Indexing complete')}
                    """)
                    
                    st.session_state.docs_uploaded += len(uploaded_files)
                else:
                    error_msg = response.text if response.text else "Unknown error"
                    st.error(f"Error: {error_msg}")
                
            except requests.exceptions.ConnectionError:
                st.error("⚠️ Cannot connect to API server. Make sure it's running on http://localhost:8000")
            except requests.exceptions.Timeout:
                st.error("⚠️ Request timeout. Files may be too large.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
            
            finally:
                status_text.empty()
                progress_bar.empty()


# ASK QUESTIONS PAGE
elif page == "❓ Ask Questions":
    st.title("❓ Ask Questions")
    
    st.markdown("Ask questions about your indexed documents. The system will retrieve relevant context and generate answers.")
    
    # Query settings
    col1, col2 = st.columns([3, 1])
    
    with col1:
        question = st.text_area(
            "Your Question",
            height=100,
            placeholder="Ask a question about your documents...",
            help="Be specific for better results"
        )
    
    with col2:
        st.markdown("### Settings")
        k = st.slider("Results Count", 1, 10, 5, help="Number of documents to retrieve")
        rephrase = st.checkbox("Rephrase Question", value=False)
    
    st.divider()
    
    # Submit button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        submit = st.button("🔍 Ask", type="primary", use_container_width=True)
    
    with col2:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    if submit and question:
        with st.spinner("Searching documents and generating answer..."):
            payload = {
                "question": question,
                "k": k,
                "use_rephrasing": rephrase
            }
            
            data, error = call_api("/ask", method="POST", json_data=payload)
            
            if data:
                # Add to message history
                st.session_state.messages.append({
                    "timestamp": datetime.now().isoformat(),
                    "question": question,
                    "response": data
                })
                
                # Display answer with prominent styling
                st.markdown('<div class="response-header">📋 RESPONSE</div>', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="success-box">
                <h3 style="margin-top: 0;">✓ Answer</h3>
                <p style="font-size: 16px; line-height: 1.8; margin: 15px 0;">
                {data.get('answer', 'No answer generated')}
                </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display metadata in highlighted boxes
                st.markdown("### 🔧 Response Details")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-box">
                    <div class="info-label">🤖 MODEL</div>
                    <div style="font-size: 18px; color: #333; margin-top: 8px; font-weight: bold;">
                    {data.get('model', 'Unknown')}
                    </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-box">
                    <div class="info-label">⚙️ MODE</div>
                    <div style="font-size: 18px; color: #333; margin-top: 8px; font-weight: bold;">
                    {data.get('mode', 'Production').upper()}
                    </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-box">
                    <div class="info-label">📚 RETRIEVED</div>
                    <div style="font-size: 18px; color: #333; margin-top: 8px; font-weight: bold;">
                    {len(data.get('retrieved_docs', []))} Documents
                    </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Show retrieved documents
                if data.get('retrieved_docs'):
                    st.markdown("---")
                    st.markdown('<div class="response-header">📚 RETRIEVED DOCUMENTS</div>', unsafe_allow_html=True)
                    
                    for idx, doc in enumerate(data.get('retrieved_docs', []), 1):
                        score = 1 / (1 + doc.get('distance', 0))
                        
                        # Color code by relevance score
                        if score > 0.7:
                            color = "#4CAF50"  # Green
                            emoji = "🔥"
                        elif score > 0.5:
                            color = "#FFA500"  # Orange
                            emoji = "⭐"
                        else:
                            color = "#2196F3"  # Blue
                            emoji = "📌"
                        
                        with st.expander(f"{emoji} Document {idx} - Relevance: {score:.2%}"):
                            st.markdown(f"""
                            <div style="background-color: {color}20; padding: 15px; border-left: 4px solid {color}; border-radius: 5px;">
                            <b style="color: {color};">Relevance Score: {score:.2%}</b>
                            <p style="color: #333; font-size: 15px; line-height: 1.6; margin-top: 10px;">
                            {doc.get('text', 'N/A')[:800]}
                            </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if doc.get('metadata'):
                                st.markdown("**Metadata:**")
                                st.json(doc['metadata'])
            else:
                st.error(f"Error: {error}")
    
    # Message history
    if st.session_state.messages:
        st.divider()
        st.markdown('<div class="response-header">📜 CONVERSATION HISTORY</div>', unsafe_allow_html=True)
        
        for i, msg in enumerate(st.session_state.messages[-5:], 1):  # Show last 5
            with st.expander(f"💬 Q{i}: {msg['question'][:60]}..."):
                st.markdown(f"""
                <div style="background-color: #E3F2FD; padding: 15px; border-left: 4px solid #2196F3; border-radius: 5px; margin-bottom: 15px;">
                <b style="color: #1976D2;">Question:</b>
                <p style="color: #333; margin: 8px 0;">{msg['question']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background-color: #E8F5E9; padding: 15px; border-left: 4px solid #4CAF50; border-radius: 5px;">
                <b style="color: #2E7D32;">Answer:</b>
                <p style="color: #333; margin: 8px 0; line-height: 1.6;">{msg['response'].get('answer', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.caption(f"⏰ {msg['timestamp']}")


# SEARCH PAGE
elif page == "🔍 Search":
    st.title("🔍 Search Documents")
    
    st.markdown("Search for documents semantically similar to your query.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Search Query",
            placeholder="Enter search terms or concepts..."
        )
    
    with col2:
        st.markdown("### Options")
        num_results = st.slider("Top Results", 1, 20, 5)
    
    if search_query and st.button("🔎 Search", type="primary"):
        with st.spinner("Searching..."):
            payload = {
                "query": search_query,
                "k": num_results
            }
            
            data, error = call_api("/search", method="POST", json_data=payload)
            
            if data:
                results = data.get('results', [])
                st.markdown(f"### Found {len(results)} Results")
                
                for idx, result in enumerate(results, 1):
                    with st.expander(f"📄 Result {idx} - Score: {result.get('distance', 0):.3f}"):
                        st.text(result.get('text', 'N/A'))
                        if result.get('metadata'):
                            st.json(result['metadata'])
            else:
                st.error(f"Search failed: {error}")


# ANALYTICS PAGE
elif page == "📈 Analytics":
    st.title("📈 Analytics & Monitoring")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Stats"):
            pass
    
    # System Statistics
    st.markdown("### 📊 System Statistics")
    
    data, error = call_api("/stats")
    
    if data:
        col1, col2, col3, col4 = st.columns(4)
        
        stats = data.get("vector_store", {})
        
        with col1:
            st.metric(
                "📚 Total Documents",
                stats.get("total_vectors", 0)
            )
        
        with col2:
            st.metric(
                "🔍 Embedding Dimension",
                stats.get("embedding_dimension", 0)
            )
        
        with col3:
            st.metric(
                "💾 Index Type",
                stats.get("index_type", "Unknown")
            )
        
        with col4:
            st.metric(
                "📍 Store Path",
                stats.get("path", "N/A")[-30:]
            )
        
        st.divider()
        
        # Configuration
        st.markdown("### ⚙️ Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Model Settings**
            - Model: gpt-4o
            - Temperature: 0.7
            - Max Tokens: 1000
            """)
        
        with col2:
            config = data.get("config", {})
            st.markdown(f"""
            **Retrieval Settings**
            - Top-K Results: {config.get('top_k', 5)}
            - Chunk Size: {config.get('chunk_size', 512)}
            - Chunk Overlap: {config.get('chunk_overlap', 50)}
            """)
    
    st.divider()
    
    # Usage Statistics
    st.markdown("### 📊 Usage Statistics")
    
    usage_data = {
        "Questions Asked": len(st.session_state.messages),
        "Documents Uploaded": st.session_state.docs_uploaded,
        "Session Active": "Yes",
    }
    
    usage_df = pd.DataFrame([usage_data])
    st.table(usage_df)


# SETTINGS PAGE
elif page == "⚙️ Settings":
    st.title("⚙️ Settings & Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Mode")
        mode = st.selectbox(
            "System Mode",
            ["Production", "Demo"],
            index=0 if st.session_state.mode == "Production" else 1,
            help="Production uses real document retrieval. Demo uses static responses."
        )
        st.session_state.mode = mode
    
    with col2:
        st.markdown("### 🔑 API Configuration")
        api_url = st.text_input(
            "API Base URL",
            value=API_BASE_URL,
            help="URL of the FastAPI server"
        )
        if api_url != API_BASE_URL:
            st.warning("Please restart app to apply changes")
    
    st.divider()
    
    st.markdown("### 📋 System Information")
    
    system_info = {
        "Current Mode": st.session_state.mode,
        "API Server": API_BASE_URL,
        "Frontend": "Streamlit",
        "Python Version": "3.12",
        "Start Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    info_df = pd.DataFrame([system_info])
    st.table(info_df)
    
    st.divider()
    
    # Danger Zone
    st.markdown("### ⚠️ Danger Zone")
    
    if st.button("🗑️ Clear All Documents", help="This cannot be undone"):
        with st.spinner("Clearing..."):
            data, error = call_api("/clear", method="POST")
            if data:
                st.success("✓ Vector store cleared!")
            else:
                st.error(f"Error clearing store: {error}")
    
    st.markdown("---")
    st.markdown("""
    **Enterprise LLMOps RAG v1.0**
    
    A production-ready Retrieval-Augmented Generation system with:
    - Document management and indexing
    - Vector similarity search
    - LLM-powered question answering
    - Enterprise analytics and monitoring
    """)
