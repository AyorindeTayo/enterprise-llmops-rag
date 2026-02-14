"""
RAG Engine Usage Examples

Demonstrates how to use the RAG Engine for document indexing and question answering.
"""

from rag_engine import RAGEngine, create_rag_engine, RAGConfig


def example_basic_usage():
    """Basic RAG Engine usage."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic RAG Engine Usage")
    print("=" * 60)
    
    # Create a RAG engine with default config
    engine = create_rag_engine(
        model_name="gpt-4o",
        temperature=0.7,
    )
    
    # Sample documents
    documents = [
        "Python is a high-level, interpreted programming language.",
        "Machine learning is a subset of artificial intelligence.",
        "FAISS is a library for efficient similarity search and clustering.",
    ]
    
    # Index documents
    print("\nIndexing documents...")
    count = engine.index_documents(documents)
    print(f"✓ Indexed {count} documents")
    
    # Ask a question
    print("\nAsking question...")
    result = engine.ask("What is Python?")
    print(f"Question: {result['question']}")
    print(f"Answer: {result['answer']}")
    print(f"Retrieved docs: {len(result['retrieved_docs'])}")


def example_with_config():
    """RAG Engine with custom configuration."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Custom Configuration")
    print("=" * 60)
    
    # Create configuration
    config = RAGConfig(
        model_name="gpt-4o",
        temperature=0.3,  # More deterministic
        max_tokens=500,
        top_k=3,
        chunk_size=256,
        chunk_overlap=32,
    )
    
    # Create engine with config
    engine = RAGEngine(config=config)
    
    # Index documents with metadata
    documents = [
        "FastAPI is a modern Python web framework.",
        "Docker containerizes applications for deployment.",
    ]
    
    metadata = [
        {"source": "framework_docs", "version": "1.0"},
        {"source": "devops_docs", "version": "2.0"},
    ]
    
    print("\nIndexing with metadata...")
    engine.index_documents(documents, metadata=metadata)
    print("✓ Documents indexed with metadata")
    
    # Get stats
    print("\nEngine Statistics:")
    stats = engine.get_stats()
    print(f"  Model: {stats['model']}")
    print(f"  Temperature: {stats['temperature']}")
    print(f"  Embedding Dim: {stats['embedding_dim']}")
    print(f"  Top-K: {stats['config']['top_k']}")


def example_batch_operations():
    """Batch processing with RAG Engine."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Batch Operations")
    print("=" * 60)
    
    engine = create_rag_engine()
    
    # Index multiple documents
    documents = [
        "Kubernetes orchestrates containerized applications.",
        "REST API enables client-server communication.",
        "Vector databases enable semantic search.",
    ]
    
    print("\nIndexing documents...")
    engine.index_documents(documents)
    print(f"✓ Indexed {len(documents)} documents")
    
    # Batch ask questions
    questions = [
        "What is Kubernetes?",
        "What is REST API?",
        "What are vector databases?",
    ]
    
    print("\nAsking multiple questions...")
    results = engine.batch_ask(questions, top_k=1)
    
    for result in results:
        print(f"\nQ: {result['question']}")
        print(f"A: {result['answer']}")


def example_document_chunking():
    """Document chunking with RAG Engine."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Document Chunking")
    print("=" * 60)
    
    config = RAGConfig(
        chunk_size=200,
        chunk_overlap=50,
    )
    
    engine = RAGEngine(config=config)
    
    # Long document
    long_doc = """
    Artificial Intelligence (AI) is transforming industries. Machine Learning (ML) 
    is a subset of AI that focuses on algorithms. Deep Learning (DL) uses neural networks
    with multiple layers. Natural Language Processing (NLP) enables computers to understand
    human language. Computer Vision (CV) allows machines to interpret visual information.
    Reinforcement Learning (RL) trains agents through rewards and penalties.
    """
    
    print("\nIndexing with chunking...")
    engine.index_documents([long_doc], chunk=True)
    
    stats = engine.get_stats()
    print(f"✓ Document chunked and indexed")
    print(f"  Chunk size: {stats['config']['chunk_size']}")
    print(f"  Chunk overlap: {stats['config']['chunk_overlap']}")


def example_error_handling():
    """Error handling with RAG Engine."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Error Handling")
    print("=" * 60)
    
    engine = create_rag_engine()
    
    # Ask question without indexed documents
    print("\nAsking question without indexed documents...")
    result = engine.ask("What should be the answer?")
    
    if "error" in result and result["error"]:
        print("✓ Error handled gracefully")
        print(f"  Message: {result['answer']}")
    else:
        print("✓ Got response even without documents")
        print(f"  Answer: {result['answer']}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RAG ENGINE USAGE EXAMPLES")
    print("=" * 60)
    
    try:
        example_basic_usage()
        example_with_config()
        example_batch_operations()
        example_document_chunking()
        example_error_handling()
        
        print("\n" + "=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        print("Note: Set OPENAI_API_KEY to run actual LLM examples")
