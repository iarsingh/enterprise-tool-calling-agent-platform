from fastapi.testclient import TestClient
from enttools.main import app

client = TestClient(app)


def test_lists_and_refuses_apply():
    assert "policy.check" in client.get("/tools").json()["tools"]
    ok = client.post("/call", json={"name": "policy.check", "arguments": {"q": "status"}}).json()
    assert ok["ok"] is True
    assert ok["applied"] is False
    refused = client.post("/call", json={"name": "catalog.search", "arguments": {"cmd": "kubectl apply"}}).json()
    assert refused["ok"] is False
