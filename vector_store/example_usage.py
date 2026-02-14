"""
Example usage of the FAISS vector store for RAG pipelines.
"""

import numpy as np
from faiss_store import FaissStore


def example_basic_usage():
    """Basic usage example."""
    print("=" * 50)
    print("BASIC USAGE EXAMPLE")
    print("=" * 50)
    
    # Initialize vector store
    vector_store = FaissStore(dim=1536, path="vector_store/documents.index")
    
    # Sample embeddings and documents
    sample_texts = [
        "Python is a versatile programming language",
        "Machine learning models require training data",
        "Vector databases enable semantic search",
        "FAISS is Facebook's similarity search library"
    ]
    
    # Create random embeddings (in practice, use real embeddings from OpenAI, HuggingFace, etc.)
    sample_embeddings = np.random.randn(len(sample_texts), 1536).astype(np.float32)
    
    # Add to vector store
    vector_store.add(sample_embeddings, sample_texts)
    print(f"Added {len(sample_texts)} documents")
    
    # Search
    query_embedding = np.random.randn(1, 1536).astype(np.float32)
    results, distances, indices = vector_store.search(query_embedding, k=2)
    
    print("\nSearch Results:")
    for i, (text, dist) in enumerate(zip(results, distances)):
        print(f"  {i+1}. {text} (distance: {dist:.4f})")
    
    # Get statistics
    print(f"\nVector Store Stats: {vector_store.get_stats()}")


def example_with_metadata():
    """Example with metadata."""
    print("\n" + "=" * 50)
    print("USAGE WITH METADATA")
    print("=" * 50)
    
    vector_store = FaissStore(dim=384, path="vector_store/with_metadata.index")
    
    texts = [
        "Customer bought laptop on 2024-01-15",
        "Order shipped to New York",
        "Invoice paid via credit card"
    ]
    
    metadata = [
        {"source": "order_system", "customer_id": "C001", "date": "2024-01-15"},
        {"source": "shipping_system", "tracking_id": "SHIP123", "destination": "NY"},
        {"source": "billing_system", "invoice_id": "INV001", "amount": 999.99}
    ]
    
    embeddings = np.random.randn(len(texts), 384).astype(np.float32)
    vector_store.add(embeddings, texts, metadata)
    
    # Search with metadata
    query_embedding = np.random.randn(1, 384).astype(np.float32)
    results = vector_store.search_with_metadata(query_embedding, k=2)
    
    print("\nSearch Results with Metadata:")
    for result in results:
        print(f"  Text: {result['text']}")
        print(f"  Distance: {result['distance']:.4f}")
        print(f"  Metadata: {result['metadata']}")
        print()


def example_batch_operations():
    """Example with batch operations."""
    print("\n" + "=" * 50)
    print("BATCH OPERATIONS EXAMPLE")
    print("=" * 50)
    
    vector_store = FaissStore(dim=768, path="vector_store/batch.index")
    
    # Batch 1
    texts_batch1 = [f"Document {i}" for i in range(1, 101)]
    embeddings_batch1 = np.random.randn(100, 768).astype(np.float32)
    vector_store.add(embeddings_batch1, texts_batch1)
    print(f"Added batch 1: {len(texts_batch1)} documents")
    
    # Batch 2
    texts_batch2 = [f"Article {i}" for i in range(101, 201)]
    embeddings_batch2 = np.random.randn(100, 768).astype(np.float32)
    vector_store.add(embeddings_batch2, texts_batch2)
    print(f"Added batch 2: {len(texts_batch2)} documents")
    
    print(f"Total vectors: {len(vector_store)}")


def example_ivf_index():
    """Example using IVFFlat for large-scale datasets."""
    print("\n" + "=" * 50)
    print("IVF INDEX EXAMPLE (Large-scale)")
    print("=" * 50)
    
    # IVF is optimized for large datasets
    vector_store = FaissStore(dim=1536, path="vector_store/large_scale.index", use_ivf=True)
    
    # Simulate large dataset
    num_documents = 10000
    texts = [f"Document with ID {i}" for i in range(num_documents)]
    embeddings = np.random.randn(num_documents, 1536).astype(np.float32)
    
    vector_store.add(embeddings, texts)
    print(f"Added {num_documents} documents to IVF index")
    
    # Search
    query_embedding = np.random.randn(1, 1536).astype(np.float32)
    results, distances, _ = vector_store.search(query_embedding, k=5)
    
    print("\nTop 5 results:")
    for text, dist in zip(results, distances):
        print(f"  {text} (distance: {dist:.4f})")


def example_rag_pipeline():
    """Example of FAISS in a RAG pipeline."""
    print("\n" + "=" * 50)
    print("RAG PIPELINE EXAMPLE")
    print("=" * 50)
    
    # Initialize vector store for RAG
    rag_store = FaissStore(dim=1536, path="vector_store/rag_documents.index")
    
    # Knowledge base documents
    knowledge_base = [
        "OpenAI's GPT-4 is a large language model with 100 trillion parameters",
        "Machine learning requires labeled training data for supervised learning",
        "Vector embeddings represent text as numerical vectors in high-dimensional space",
        "RAG combines retrieval and generation for knowledge-grounded responses",
        "FAISS provides fast similarity search for large-scale embeddings"
    ]
    
    # In a real scenario, these would come from an embedding model
    embeddings = np.random.randn(len(knowledge_base), 1536).astype(np.float32)
    
    # Store documents
    rag_store.add(embeddings, knowledge_base)
    print(f"Stored {len(knowledge_base)} documents in knowledge base")
    
    # User query
    user_query = "How does RAG work?"
    query_embedding = np.random.randn(1, 1536).astype(np.float32)
    
    # Retrieve relevant documents
    relevant_docs, distances, _ = rag_store.search(query_embedding, k=3)
    
    print(f"\nUser Query: '{user_query}'")
    print("\nRetrieved Documents:")
    for i, (doc, dist) in enumerate(zip(relevant_docs, distances)):
        print(f"  {i+1}. {doc} (similarity: {1/(1+dist):.4f})")
    
    print("\n[In a full RAG pipeline, these would be passed to an LLM for generation]")


if __name__ == "__main__":
    # Run examples
    example_basic_usage()
    example_with_metadata()
    example_batch_operations()
    example_ivf_index()
    example_rag_pipeline()
    
    print("\n" + "=" * 50)
    print("All examples completed!")
    print("=" * 50)
