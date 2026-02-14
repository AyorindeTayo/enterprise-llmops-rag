"""
RAG Engine Module for Retrieval-Augmented Generation

This module provides the core RAG (Retrieval-Augmented Generation) engine
that combines document retrieval with LLM-based generation for knowledge-grounded
question answering.

Features:
- Document indexing and retrieval using FAISS
- LLM-based answer generation using OpenAI
- Batch processing support
- Configurable models and parameters
- Metadata management for retrieved documents
"""

__version__ = "1.0.0"
__author__ = "LLMOps Team"
__all__ = [
    "RAGEngine",
    "create_rag_engine",
    "RAGConfig",
]

import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class RAGConfig:
    """Configuration class for RAG Engine."""
    
    def __init__(
        self,
        model_name: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        embedding_model: str = "text-embedding-3-large",
        embedding_dim: int = 1536,
        vector_store_path: str = "vector_store/documents.index",
        top_k: int = 5,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ):
        """
        Initialize RAG configuration.
        
        Args:
            model_name: LLM model to use
            temperature: Generation temperature (0-1)
            max_tokens: Maximum tokens in response
            embedding_model: Embedding model name
            embedding_dim: Embedding dimension
            vector_store_path: Path to FAISS vector store
            top_k: Number of documents to retrieve
            chunk_size: Document chunk size
            chunk_overlap: Overlap between chunks
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.embedding_model = embedding_model
        self.embedding_dim = embedding_dim
        self.vector_store_path = vector_store_path
        self.top_k = top_k
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap


class RAGEngine:
    """
    Retrieval-Augmented Generation Engine.
    
    Combines document retrieval with LLM-based generation for
    knowledge-grounded question answering.
    """
    
    def __init__(
        self,
        config: Optional[RAGConfig] = None,
        model_name: str = "gpt-4o",
        temperature: float = 0.7,
        vector_store_path: str = "vector_store/documents.index",
    ):
        """
        Initialize RAG Engine.
        
        Args:
            config: RAGConfig instance
            model_name: LLM model name (used if config not provided)
            temperature: Generation temperature (used if config not provided)
            vector_store_path: Path to vector store (used if config not provided)
        """
        # Use provided config or create from parameters
        if config is None:
            config = RAGConfig(
                model_name=model_name,
                temperature=temperature,
                vector_store_path=vector_store_path,
            )
        
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize engine components."""
        try:
            # Lazy import to avoid requiring all dependencies at import time
            from vector_store.faiss_store import FaissStore
            from services.llm_service import _get_client
            from embeddings.embed import embed_texts
            
            # Initialize vector store
            self.vector_store = FaissStore(
                dim=self.config.embedding_dim,
                path=self.config.vector_store_path,
            )
            
            # Store embedding function
            self.embed_texts = embed_texts
            
            # Store LLM client getter
            self._get_llm_client = _get_client
            
            self.logger.info(f"RAG Engine initialized with {self.config.model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG engine: {str(e)}")
            raise
    
    def index_documents(
        self,
        documents: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None,
        chunk: bool = False,
    ) -> int:
        """
        Index documents into the vector store.
        
        Args:
            documents: List of documents to index
            metadata: Optional metadata for each document
            chunk: Whether to chunk documents
            
        Returns:
            Number of documents indexed
        """
        try:
            docs_to_index = documents
            
            # Optionally chunk documents
            if chunk:
                docs_to_index = self._chunk_documents(documents)
            
            # Embed documents
            embeddings = self.embed_texts(docs_to_index)
            
            # Add to vector store
            self.vector_store.add(embeddings, docs_to_index, metadata)
            
            self.logger.info(f"Indexed {len(docs_to_index)} documents")
            return len(docs_to_index)
            
        except Exception as e:
            self.logger.error(f"Error indexing documents: {str(e)}")
            raise
    
    def ask(
        self,
        question: str,
        top_k: Optional[int] = None,
        use_context: bool = True,
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG.
        
        Args:
            question: Question to answer
            top_k: Number of documents to retrieve
            use_context: Whether to use retrieved context
            
        Returns:
            Dictionary with answer, context, and metadata
        """
        try:
            k = top_k or self.config.top_k
            
            # Retrieve relevant documents
            question_embedding = self.embed_texts([question])[0:1]
            retrieved = self.vector_store.search_with_metadata(question_embedding, k=k)
            
            # Extract context
            context = "\n".join([r["text"] for r in retrieved])
            
            if not use_context or not context:
                answer = self._generate_answer(question, "")
            else:
                answer = self._generate_answer(question, context)
            
            return {
                "question": question,
                "answer": answer,
                "context": context,
                "retrieved_docs": retrieved,
                "model": self.config.model_name,
            }
            
        except Exception as e:
            self.logger.error(f"Error answering question: {str(e)}")
            return {
                "question": question,
                "answer": f"Error: {str(e)}",
                "context": "",
                "retrieved_docs": [],
                "error": True,
            }
    
    def batch_ask(
        self,
        questions: List[str],
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Answer multiple questions.
        
        Args:
            questions: List of questions
            top_k: Number of documents per question
            
        Returns:
            List of answer dictionaries
        """
        results = []
        for question in questions:
            result = self.ask(question, top_k=top_k)
            results.append(result)
        return results
    
    def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer using LLM."""
        try:
            from services.llm_service import generate_answer
            return generate_answer(question, context, self.config.model_name, self.config.temperature)
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def _chunk_documents(self, documents: List[str]) -> List[str]:
        """
        Chunk documents into smaller pieces.
        
        Args:
            documents: Documents to chunk
            
        Returns:
            Chunked documents
        """
        chunked = []
        for doc in documents:
            chunks = self._chunk_text(
                doc,
                chunk_size=self.config.chunk_size,
                overlap=self.config.chunk_overlap,
            )
            chunked.extend(chunks)
        return chunked
    
    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Chunk text into overlapping pieces.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        step = chunk_size - overlap
        
        for i in range(0, len(text), step):
            chunk = text[i : i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG engine statistics."""
        return {
            "model": self.config.model_name,
            "temperature": self.config.temperature,
            "embedding_dim": self.config.embedding_dim,
            "vector_store": self.vector_store.get_stats(),
            "config": {
                "top_k": self.config.top_k,
                "chunk_size": self.config.chunk_size,
                "chunk_overlap": self.config.chunk_overlap,
            },
        }
    
    def clear(self):
        """Clear all indexed documents."""
        self.vector_store.clear()
        self.logger.info("RAG engine cleared")


def create_rag_engine(
    model_name: str = "gpt-4o",
    temperature: float = 0.7,
    vector_store_path: str = "vector_store/documents.index",
    embedding_dim: int = 1536,
    top_k: int = 5,
) -> RAGEngine:
    """
    Factory function to create a RAGEngine instance.
    
    Args:
        model_name: LLM model to use
        temperature: Generation temperature
        vector_store_path: Path to vector store
        embedding_dim: Embedding dimension
        top_k: Number of documents to retrieve
        
    Returns:
        Configured RAGEngine instance
    """
    config = RAGConfig(
        model_name=model_name,
        temperature=temperature,
        vector_store_path=vector_store_path,
        embedding_dim=embedding_dim,
        top_k=top_k,
    )
    return RAGEngine(config=config)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger.debug(f"RAG Engine v{__version__} loaded successfully")
