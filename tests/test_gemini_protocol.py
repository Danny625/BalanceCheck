"""Exercise the actual installed Google SDK over a local mock HTTP transport."""
import json

from google import genai
import httpx2 as httpx

from agent import DEFAULT_MODEL, check_connection, review
from data import load_scenario
from tests.test_agent import example_report


def test_real_sdk_serializes_tool_round_trip_and_structured_report():
    requests = []

    def respond(request):
        body = json.loads(request.content)
        requests.append(body)
        if len(requests) == 1:
            calls = [("get_review_rules", {}), ("get_performance", {})]
            calls += [(name, {"character": character}) for character in ["Vex", "Brannoc", "Lyra", "Okoro", "Sable", "Quill"]
                      for name in ["get_character_context", "get_feedback"]]
            steps = [{"type": "function_call", "id": f"f{i}", "name": name, "arguments": args} for i, (name, args) in enumerate(calls)]
        else:
            text = json.dumps(example_report()) if "response_format" in body else "READY"
            steps = [{"type": "model_output", "content": [{"type": "text", "text": text}]}]
        return httpx.Response(200, headers={"content-type": "application/json"}, json={
            "id": "offline-protocol-test", "model": DEFAULT_MODEL, "status": "completed",
            "created": "2026-11-20T00:00:00Z", "updated": "2026-11-20T00:00:00Z", "steps": steps})

    client = genai.Client(api_key="offline-protocol-placeholder")
    transport = httpx.Client(transport=httpx.MockTransport(respond))
    client.interactions.sdk_configuration.client = transport
    try:
        result = review(load_scenario(), "offline-protocol-placeholder", client=client)
    finally:
        transport.close()
        client.close()
    assert result["status"] == "valid", result
    assert len(requests) == 3
    assert all(request["store"] is False for request in requests)
    assert "function_result" in json.dumps(requests[1]["input"])
    assert requests[-1]["response_format"]["mime_type"] == "application/json"


def test_model_metadata_check_uses_real_sdk_without_generation(monkeypatch):
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(200, headers={"content-type": "application/json"}, json={
            "models": [{"name": "models/" + DEFAULT_MODEL, "supportedGenerationMethods": ["generateContent"]}]})

    client = genai.Client(api_key="offline-metadata-placeholder")
    client._api_client._httpx_client = httpx.Client(transport=httpx.MockTransport(respond))
    monkeypatch.setattr(genai, "Client", lambda **kwargs: client)
    result = check_connection("offline-metadata-placeholder")
    assert result["ok"] and result["selected_model_listed"]
    assert len(requests) == 1 and requests[0].method == "GET"
