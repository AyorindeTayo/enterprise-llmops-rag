from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import os
import sys
from pathlib import Path
import tempfile
import shutil

# Ensure app directory is in path for imports
app_dir = Path(__file__).parent.parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# Load environment first
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass

from agents.qa_agent import answer_question, index_knowledge_base, search_knowledge_base, get_qa_stats
from services.retriever import get_vector_store

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Enterprise LLMOps RAG API",
    description="Production-ready RAG API with vector search and LLM-based QA",
    version="1.0.0"
)

# Configuration
USE_DEMO_MODE = os.getenv("USE_DEMO_MODE", "true").lower() == "true"
TEMP_UPLOAD_DIR = Path(tempfile.gettempdir()) / "rag_uploads"
TEMP_UPLOAD_DIR.mkdir(exist_ok=True)


class AskRequest(BaseModel):
    question: str
    k: int = 5
    use_rephrasing: bool = False


class IndexRequest(BaseModel):
    documents: List[str]
    metadata: Optional[List[dict]] = None



class SearchRequest(BaseModel):
    query: str
    k: int = 5


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "API is running",
        "demo_mode": USE_DEMO_MODE
    }


@app.get("/stats")
def stats():
    """Get vector store statistics."""
    try:
        return get_qa_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index")
def index_docs(req: IndexRequest):
    """Index documents into the vector store."""
    try:
        result = index_knowledge_base(req.documents, req.metadata)
        if result["status"] == "success":
            return {
                "status": "success",
                "indexed": result["indexed_count"],
                "message": f"Successfully indexed {result['indexed_count']} documents"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Indexing failed"))
    except Exception as e:
        logger.error(f"Error indexing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
def ask(req: AskRequest):
    """Answer a question using RAG."""
    try:
        # In demo mode, use demo answers
        if USE_DEMO_MODE:
            from services.llm_service import _get_demo_answer
            from datetime import datetime
            
            # Build context from the question itself for demo
            context = f"Current date: {datetime.now().strftime('%B %d, %Y')}"
            answer = _get_demo_answer(req.question, context)
            
            return {
                "question": req.question,
                "answer": answer,
                "mode": "demo"
            }
        else:
            answer = answer_question(
                question=req.question,
                k=req.k,
                use_rephrasing=req.use_rephrasing
            )
            return {
                "question": req.question,
                "answer": answer
            }
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
def search(req: SearchRequest):
    """Search for similar documents."""
    try:
        results = search_knowledge_base(req.query, k=req.k)
        return {
            "query": req.query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear")
def clear_store():
    """Clear all documents from the vector store."""
    try:
        store = get_vector_store()
        store.clear()
        return {"status": "success", "message": "Vector store cleared"}
    except Exception as e:
        logger.error(f"Error clearing store: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload_documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and index documents from files."""
    try:
        uploaded_docs = []
        uploaded_metadata = []
        
        for file in files:
            try:
                # Save file temporarily
                temp_path = TEMP_UPLOAD_DIR / file.filename
                
                with open(temp_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # Try to process with document processor
                try:
                    from frontend_streamlit.document_processor import DocumentProcessor
                    chunks, metadata = DocumentProcessor.process_file(str(temp_path))
                    uploaded_docs.extend(chunks)
                    uploaded_metadata.extend(metadata)
                except Exception as e:
                    # Fallback: just use file content as text
                    logger.warning(f"Could not process {file.filename} with DocumentProcessor: {str(e)}")
                    content_str = content.decode('utf-8', errors='ignore')
                    if content_str.strip():
                        uploaded_docs.append(content_str)
                        uploaded_metadata.append({
                            "filename": file.filename,
                            "file_size": len(content),
                            "type": file.content_type
                        })
                
                # Clean up temp file
                temp_path.unlink(missing_ok=True)
                
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                continue
        
        # Index documents
        if uploaded_docs:
            result = index_knowledge_base(uploaded_docs, uploaded_metadata)
            
            return {
                "status": "success",
                "files_processed": len(files),
                "documents_indexed": len(uploaded_docs),
                "chunks_created": len(uploaded_docs),
                "message": f"Indexed {len(uploaded_docs)} document chunks from {len(files)} files"
            }
        else:
            return {
                "status": "error",
                "message": "No valid documents found in uploaded files"
            }
            
    except Exception as e:
        logger.error(f"Error uploading documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    """Root endpoint with API info."""
    return {
        "message": "Welcome to Enterprise LLMOps RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "demo_mode": USE_DEMO_MODE,
        "endpoints": {
            "health": "GET /health",
            "ask": "POST /ask",
            "index": "POST /index",
            "search": "POST /search",
            "upload": "POST /upload_documents",
            "stats": "GET /stats",
            "clear": "POST /clear"
        }
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

