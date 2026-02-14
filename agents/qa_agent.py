"""Question Answering agent for RAG pipeline."""

import logging
import sys
from pathlib import Path
from typing import Optional

# Ensure app directory is in path
_app_path = str(Path(__file__).parent.parent.absolute())
if _app_path not in sys.path:
    sys.path.insert(0, _app_path)

from services.retriever import retrieve_context, index_documents, search_similar, get_store_stats
from services.llm_service import generate_answer, rephrase_question

logger = logging.getLogger(__name__)


def answer_question(question: str, k: int = 5, use_rephrasing: bool = False) -> str:
    """
    Answer a question using RAG (Retrieval-Augmented Generation).
    
    Args:
        question: User's question
        k: Number of documents to retrieve
        use_rephrasing: Whether to rephrase the question for better retrieval
        
    Returns:
        Generated answer
    """
    try:
        # Optionally rephrase the question for better retrieval
        search_query = question
        if use_rephrasing:
            search_query = rephrase_question(question)
            logger.info(f"Rephrased question: {search_query}")
        
        # Retrieve relevant context
        context = retrieve_context(search_query, k=k)
        logger.info(f"Retrieved context for question: {question}")
        
        # Generate answer based on context
        answer = generate_answer(question, context)
        
        return answer
        
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        return f"Error processing question: {str(e)}"


def batch_answer_questions(questions: list[str], k: int = 5) -> list[dict]:
    """
    Answer multiple questions in batch.
    
    Args:
        questions: List of questions
        k: Number of documents to retrieve per question
        
    Returns:
        List of dicts with question and answer
    """
    results = []
    for question in questions:
        answer = answer_question(question, k=k)
        results.append({
            "question": question,
            "answer": answer
        })
    return results


def index_knowledge_base(documents: list[str], metadata: list[dict] = None) -> dict:
    """
    Index documents into the knowledge base.
    
    Args:
        documents: List of documents to index
        metadata: Optional metadata for documents
        
    Returns:
        Indexing result with count
    """
    try:
        count = index_documents(documents, metadata)
        logger.info(f"Indexed {count} documents")
        return {"status": "success", "indexed_count": count}
    except Exception as e:
        logger.error(f"Error indexing documents: {str(e)}")
        return {"status": "error", "message": str(e)}


def search_knowledge_base(query: str, k: int = 5) -> list[dict]:
    """
    Search the knowledge base for relevant documents.
    
    Args:
        query: Search query
        k: Number of results to return
        
    Returns:
        List of similar documents with scores
    """
    try:
        results = search_similar(query, k=k)
        return results
    except Exception as e:
        logger.error(f"Error searching knowledge base: {str(e)}")
        return []


def get_qa_stats() -> dict:
    """Get statistics about the QA system."""
    try:
        stats = get_store_stats()
        return {
            "status": "ok",
            "vector_store": stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {"status": "error", "message": str(e)}
