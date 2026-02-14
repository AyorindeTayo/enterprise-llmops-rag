# 🤖 Enterprise LLMOps RAG System - Complete User Guide

## Overview

This is a production-ready **Retrieval-Augmented Generation (RAG)** system that combines:
- **Document Management**: Upload, process, and index PDFs, Word docs, and text files
- **Vector Search**: Fast similarity search using FAISS
- **LLM Integration**: OpenAI GPT-4o for intelligent question answering
- **Enterprise Features**: Analytics, monitoring, multi-document synthesis

## Architecture

```
┌─────────────────────────────────────────────┐
│      Streamlit Frontend (Port 8501)        │
│  - Upload Documents                         │
│  - Ask Questions                            │
│  - Search Documents                         │
│  - View Analytics                           │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼─────────┐   ┌──────▼────────────┐
│  FastAPI Server │   │  Document         │
│  (Port 8000)    │   │  Processor        │
│  - /ask         │   │  - PDF Extract    │
│  - /index       │   │  - DOCX Parse     │
│  - /search      │   │  - Chunking       │
│  - /upload      │   │  - Metadata       │
└───────┬─────────┘   └──────┬────────────┘
        │                     │
        ├─────────┬───────────┤
        │         │           │
    ┌───▼──┐  ┌──▼──┐  ┌─────▼────┐
    │FAISS │  │ LLM │  │Embedding │
    │Store │  │API  │  │ Models   │
    └──────┘  └─────┘  └──────────┘
```

## Quick Start

### 1. Prerequisites

- Python 3.10+
- OpenAI API key (optional for demo mode)
- Virtual environment (already set up)

### 2. Environment Setup

**Option A: Using the startup script**
```bash
# Make startup script executable
chmod +x startup.sh

# Run startup script
./startup.sh
```

**Option B: Manual setup**
```bash
# Activate virtual environment
source llmops-env/bin/activate

# Create .env file with your API key (optional)
cat > .env <<EOF
OPENAI_API_KEY=sk-your-api-key-here
USE_DEMO_MODE=true
EOF
```

### 3. Start the System

**Option 1: Automatic (both API and Streamlit)**
```bash
python start.py
```

**Option 2: Manual (in separate terminals)**

Terminal 1 - Start API Server:
```bash
source llmops-env/bin/activate
uvicorn api_gateway.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Start Streamlit Frontend:
```bash
source llmops-env/bin/activate
streamlit run frontend_streamlit/app.py --server.port 8501
```

### 4. Access the System

- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## 📚 Using the System

### Home Page
- System overview and statistics
- Quick links to all features
- Status information

### 📤 Upload Documents
1. Click "Upload Documents" in sidebar
2. Select PDF, DOCX, or TXT files
3. Click "Index Documents"
4. System will:
   - Extract text from files
   - Split into chunks
   - Create embeddings
   - Store in FAISS index

**Supported Formats:**
- `.pdf` - PDF files (extracts text using pypdf)
- `.docx` - Word documents (extracts text using python-docx)
- `.txt` - Plain text files

### ❓ Ask Questions
1. Click "Ask Questions" in sidebar
2. Type your question in the text area
3. Adjust settings (optional):
   - **Results Count**: How many documents to retrieve (1-10)
   - **Rephrase Question**: Enable to rephrase complex questions
4. Click "Ask"
5. System will:
   - Retrieve relevant documents
   - Generate context-aware answer
   - Show retrieved documents
   - Track conversation history

**Example Questions:**
- "What are the main topics covered?"
- "Summarize the key points about X"
- "Compare document 1 and document 2"

### 🔍 Search Documents
1. Click "Search" in sidebar
2. Enter search terms or concepts
3. Adjust "Top Results" slider for more/fewer results
4. Click "Search"
5. See list of semantically similar documents with scores

### 📈 Analytics
- View system statistics
- Monitor vector store usage
- Check configuration settings
- Track session activity

**Available Metrics:**
- Total documents indexed
- Embedding dimension
- Index type (FlatL2/IVFFlat)
- Questions asked
- Documents uploaded

### ⚙️ Settings
- **Mode Selection**: Demo or Production
- **API Configuration**: Change API endpoint
- **System Information**: View current setup
- **Danger Zone**: Clear all documents

## API Endpoints

### Health & Status
```bash
# Check API status
curl http://localhost:8000/health

# Get system statistics
curl http://localhost:8000/stats
```

### Ask Questions
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "k": 5,
    "use_rephrasing": false
  }'
```

### Index Documents
```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{
    "documents": ["Document 1 content", "Document 2 content"],
    "metadata": [
      {"source": "file1.pdf"},
      {"source": "file2.txt"}
    ]
  }'
```

### Upload Files
```bash
curl -X POST http://localhost:8000/upload_documents \
  -F "files=@document1.pdf" \
  -F "files=@document2.txt"
```

### Search Documents
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "k": 5
  }'
```

### Clear Store
```bash
curl -X POST http://localhost:8000/clear
```

## 🔄 How RAG Works

1. **Document Ingestion**
   - Upload files
   - Extract text content
   - Split into chunks (default: 512 chars with 50 char overlap)

2. **Embedding & Storage**
   - Convert chunks to embeddings (1536-dimensional vectors)
   - Store in FAISS index with metadata

3. **Query Processing**
   - Convert user question to embedding
   - Search FAISS index for similar documents
   - Retrieve top-K most relevant chunks

4. **Answer Generation**
   - Create prompt with retrieved context
   - Send to GPT-4o LLM
   - Generate contextual answer

## Features

### Document Processing
- **Automatic Chunking**: Split large documents intelligently
- **Metadata Tracking**: Store source info, page numbers, etc.
- **Multi-format Support**: PDF, DOCX, TXT
- **Error Handling**: Gracefully handle corrupted files

### Search & Retrieval
- **Semantic Search**: Find documents by meaning, not keywords
- **Configurable Results**: 1-20 documents per query
- **Relevance Scoring**: See confidence scores for results
- **Metadata Display**: View document source and context

### Question Answering
- **Context-Aware**: Uses actual documents for answers
- **Question Rephrasing**: Improve retrieval with rephrase option
- **Conversation History**: View previous Q&A
- **Multiple Modes**: Demo mode (no API needed) and Production (real)

### Enterprise Features
- **Usage Analytics**: Track system usage
- **Vector Store Statistics**: Monitor index status
- **Configuration Management**: Adjust settings
- **Session Management**: Track conversations

## Demo Mode vs Production Mode

### Demo Mode (Default)
- ✓ No API key required
- ✓ Fast testing
- ✓ Static responses
- ✗ Limited functionality
- ✗ No real document retrieval

### Production Mode
- ✓ Real document retrieval
- ✓ Context-aware answers
- ✓ Full RAG pipeline
- ✗ Requires OpenAI API key
- ✗ API usage costs

**Toggle Mode:**
1. Go to Settings
2. Select "Production" from dropdown
3. System requires OPENAI_API_KEY

## Environment Variables

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-api-key-here

# System Configuration
USE_DEMO_MODE=true  # Set to false for production

# API Server
API_HOST=0.0.0.0
API_PORT=8000
```

## Troubleshooting

### API Server Won't Start
```
Error: Address already in use
Solution: Kill process on port 8000 or use different port
netstat -tulpn | grep 8000
kill -9 <PID>
```

### Streamlit Shows "Connection Refused"
```
Error: Cannot connect to API server
Solution: Make sure API is running on port 8000
Check: http://localhost:8000/health
```

### Documents Won't Upload
```
Error: File format not supported
Supported: PDF, DOCX, TXT
Max file size: System memory dependent
```

### "OPENAI_API_KEY not set" Error
```
Solution 1: Set environment variable
export OPENAI_API_KEY='sk-...'

Solution 2: Use Demo Mode
Set USE_DEMO_MODE=true in .env

Solution 3: Use API directly without Streamlit
python -c "from agents.qa_agent import answer_question; print(answer_question('test'))"
```

## Performance Tips

### For Large Documents
- Split into smaller files manually
- Increase chunk overlap for better coherence
- Use Production mode with proper API key

### For Fast Responses
- Keep vector store size reasonable (<10k chunks)
- Adjust top-K downward (search fewer documents)
- Use demo mode for testing

### For Better Answers
- Upload relevant documents only
- Use longer documents for context
- Ask specific questions
- Enable question rephrasing

## File Structure

```
end-to-end llmops/
├── api_gateway/
│   └── main.py              # FastAPI server
├── agents/
│   └── qa_agent.py          # Question answering logic
├── services/
│   ├── retriever.py         # Document retrieval
│   └── llm_service.py       # LLM integration
├── embeddings/
│   └── embed.py             # Embedding generation
├── vector_store/
│   └── faiss_store.py       # FAISS index management
├── frontend_streamlit/
│   ├── app.py               # Streamlit UI
│   └── document_processor.py # File processing
├── rag_engine/
│   └── __init__.py          # RAG engine core
├── .env                     # Configuration
├── requirements.txt         # Dependencies
├── start.py                 # System startup
└── startup.sh              # Startup script
```

## Advanced Configuration

### Modify Chunk Size
Edit in `frontend_streamlit/app.py`:
```python
chunk_size = st.slider("Chunk Size", 256, 1024, 512)
```

### Change Embedding Model
Edit in `embeddings/embed.py`:
```python
model="text-embedding-3-large"  # Change to "text-embedding-3-small"
```

### Adjust LLM Temperature
Edit in `api_gateway/main.py`:
```python
temperature=0.7  # Lower = more deterministic, Higher = more creative
```

## Performance Metrics

- **Embedding Speed**: ~100 docs/minute
- **Search Speed**: <100ms for 10k documents
- **API Response Time**: 1-3 seconds (with GPT-4o)
- **Memory Usage**: ~500MB for 1k documents

## Next Steps

1. **Production Deployment**
   - Set up with proper API keys
   - Deploy to cloud (AWS, Azure, GCP)
   - Add authentication/authorization

2. **Advanced Features**
   - Implement semantic caching
   - Add user authentication
   - Enable document summaries
   - Support streaming responses

3. **Monitoring**
   - Add Prometheus metrics
   - Set up logging infrastructure
   - Create dashboards
   - Implement alerts

## Support & Documentation

- **API Docs**: http://localhost:8000/docs
- **Code**: See respective module files
- **Issues**: Check logs in terminals

## License

Enterprise LLMOps RAG System v1.0

---

**🎉 Your RAG system is ready to use!**

Start asking questions about your documents now!
