"""Quick start guide for the RAG system"""

import sys
import os
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set a dummy API key for testing (replace with real key)
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  OPENAI_API_KEY not set. Set it before using LLM features:")
    print("   export OPENAI_API_KEY='your-api-key-here'")

# Import and test
from agents.qa_agent import answer_question, index_knowledge_base, search_knowledge_base
from services.retriever import get_store_stats
from api_gateway.main import app
import uvicorn

print("✓ All imports successful!")
print("\nAvailable functions:")
print("  - answer_question(question, k=5, use_rephrasing=False)")
print("  - index_knowledge_base(documents, metadata=None)")
print("  - search_knowledge_base(query, k=5)")
print("  - get_store_stats()")

print("\nTo start the API server, run:")
print("  uvicorn api_gateway.main:app --reload --host 0.0.0.0 --port 8000")

print("\nAPI Endpoints:")
print("  POST /ask       - Answer a question")
print("  POST /index     - Index documents")
print("  POST /search    - Search knowledge base")
print("  GET  /health    - Health check")
print("  GET  /stats     - Get vector store statistics")
print("  POST /clear     - Clear vector store")

if __name__ == "__main__":
    print("\nStarting API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
