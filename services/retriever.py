"""Document retrieval service for RAG pipeline."""

import numpy as np
import sys
from pathlib import Path
from typing import List

# Ensure /app is in Python path for imports
_app_path = str(Path(__file__).parent.parent.absolute())
if _app_path not in sys.path:
    sys.path.insert(0, _app_path)

# Lazy imports - these will be done when functions are called
FaissStore = None
embed_texts = None

def _ensure_imports():
    """Ensure required modules are imported."""
    global FaissStore, embed_texts
    if FaissStore is None:
        from vector_store.faiss_store import FaissStore as FS
        FaissStore = FS
    if embed_texts is None:
        from embeddings.embed import embed_texts as et
        embed_texts = et

# Global vector store instance
_vector_store = None


def get_vector_store() -> FaissStore:
    """Get or initialize the global vector store."""
    global _vector_store
    _ensure_imports()
    if _vector_store is None:
        _vector_store = FaissStore(dim=1536, path="vector_store/documents.index")
    return _vector_store


def retrieve_context(query: str, k: int = 5) -> str:
    """
    Retrieve relevant context from the vector store based on query.
    
    Args:
        query: User question/query string
        k: Number of documents to retrieve
        
    Returns:
        Concatenated context from top-k similar documents
    """
    try:
        # Embed the query
        query_embedding = embed_texts([query])[0:1]  # Shape: (1, 1536)
        
        # Get vector store
        store = get_vector_store()
        
        # Search for similar documents
        results = store.search_with_metadata(query_embedding, k=k)
        
        # Combine results into context string
        context_parts = []
        for result in results:
            text = result.get("text", "")
            distance = result.get("distance", 0)
            if text:
                context_parts.append(f"[Score: {1/(1+distance):.2f}] {text}")
        
        context = "\n".join(context_parts) if context_parts else "No relevant context found."
        
        return context
        
    except Exception as e:
        return f"Error retrieving context: {str(e)}"


def index_documents(documents: List[str], metadata: List[dict] = None) -> int:
    """
    Index documents into the vector store.
    
    Args:
        documents: List of text documents to index
        metadata: Optional metadata for each document
        
    Returns:
        Number of documents indexed
    """
    try:
        # Embed documents
        embeddings = embed_texts(documents)
        
        # Get vector store and add documents
        store = get_vector_store()
        store.add(embeddings, documents, metadata)
        
        return len(documents)
        
    except Exception as e:
        raise Exception(f"Error indexing documents: {str(e)}")


def search_similar(query: str, k: int = 5) -> List[dict]:
    """
    Search for documents similar to the query.
    
    Args:
        query: Query string
        k: Number of results to return
        
    Returns:
        List of similar documents with metadata and scores
    """
    try:
        query_embedding = embed_texts([query])[0:1]
        store = get_vector_store()
        results = store.search_with_metadata(query_embedding, k=k)
        
        return results
        
    except Exception as e:
        raise Exception(f"Error searching similar documents: {str(e)}")


def clear_store() -> None:
    """Clear all documents from the vector store."""
    store = get_vector_store()
    store.clear()


def get_store_stats() -> dict:
    """Get statistics about the vector store."""
    store = get_vector_store()
    return store.get_stats()
