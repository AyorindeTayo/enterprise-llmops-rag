import numpy as np
import embeddings.embed as embed_mod
import requests


def test_embed_text_demo(monkeypatch):
    # Force _get_client to raise proxies TypeError so fallback is used
    def fake_get_client():
        raise TypeError("Client.__init__() got an unexpected keyword argument 'proxies'")

    monkeypatch.setattr(embed_mod, "_get_client", fake_get_client)

    class FakeResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {"data": [{"embedding": [0.1, 0.2, 0.3]}]}

    monkeypatch.setattr(requests, "post", lambda *a, **k: FakeResp())

    vec = embed_mod.embed_text("hello")
    assert isinstance(vec, np.ndarray)
    assert vec.shape[0] == 3


def test_embed_texts_batch(monkeypatch):
    def fake_get_client():
        raise TypeError("Client.__init__() got an unexpected keyword argument 'proxies'")

    monkeypatch.setattr(embed_mod, "_get_client", fake_get_client)

    class FakeResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {"data": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]}
            ]}

    monkeypatch.setattr(requests, "post", lambda *a, **k: FakeResp())

    vecs = embed_mod.embed_texts(["a", "b"])
    assert isinstance(vecs, np.ndarray)
    assert vecs.shape[0] == 2
