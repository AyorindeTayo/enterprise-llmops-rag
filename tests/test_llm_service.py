import services.llm_service as lsvc


def test_generate_answer_demo_mode():
    ans = lsvc.generate_answer("What's the date?", "some context", use_demo=True)
    assert isinstance(ans, str)
    assert "current date" in ans or "Based on the context" in ans


def test_generate_answer_fallback_http(monkeypatch):
    # Simulate _get_client raising the proxies TypeError
    def fake_get_client():
        raise TypeError("Client.__init__() got an unexpected keyword argument 'proxies'")

    monkeypatch.setattr(lsvc, "_get_client", fake_get_client)

    class FakeResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "Fallback answer"}}]}

    monkeypatch.setattr(lsvc, "requests", lsvc.requests)
    monkeypatch.setattr(lsvc.requests, "post", lambda *a, **k: FakeResp())

    ans = lsvc.generate_answer("Q?", "ctx")
    assert "Fallback answer" in ans
