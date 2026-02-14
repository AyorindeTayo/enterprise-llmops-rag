import numpy as np
import services.retriever as retriever


def test_retrieve_context_no_results(monkeypatch):
    # Mock embedding and vector store to return no results
    monkeypatch.setattr(retriever, "embed_texts", lambda texts: np.zeros((1, 1536)))

    class FakeStore:
        def search_with_metadata(self, q_emb, k=5):
            return []

    monkeypatch.setattr(retriever, "get_vector_store", lambda: FakeStore())

    ctx = retriever.retrieve_context("some query")
    assert "No relevant context found" in ctx


def test_index_documents_calls_store_add(monkeypatch):
    docs = ["doc1", "doc2"]
    # return simple embeddings
    monkeypatch.setattr(retriever, "embed_texts", lambda texts: np.ones((2, 1536)))

    called = {}

    class FakeStore:
        def add(self, embeddings, documents, metadata=None):
            called['added'] = True

    monkeypatch.setattr(retriever, "get_vector_store", lambda: FakeStore())

    n = retriever.index_documents(docs)
    assert n == 2
    assert called.get('added', False) is True
