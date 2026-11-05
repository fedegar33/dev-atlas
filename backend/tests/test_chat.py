import asyncio
import json
from functools import partial
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from openai import APIConnectionError, APITimeoutError, RateLimitError

from agent.chat import DEFAULT_MODEL, ChatAgent, create_agent
from api.main import app, get_agent


@pytest.fixture
def model():
    return AsyncMock(ainvoke=AsyncMock(return_value=AIMessage(content="¡Hola!")))


@pytest.fixture
def client(model):
    app.dependency_overrides[get_agent] = lambda: ChatAgent(model)
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_chat_passes_message_and_system_prompt_to_model(client, model):
    response = client.post("/chat", json={"message": "Hola"})
    assert response.status_code == 200
    assert response.json() == {"reply": "¡Hola!"}
    messages = model.ainvoke.call_args.args[0]
    assert [message.type for message in messages] == ["system", "human"]
    assert "DevAtlas" in messages[0].content
    assert messages[1].content == "Hola"


@pytest.mark.parametrize(
    "body",
    [{}, {"message": ""}, {"message": "  "}, {"message": 42}, {"message": "x" * 8001}],
)
def test_invalid_message_never_calls_model(client, model, body):
    assert client.post("/chat", json=body).status_code == 422
    model.ainvoke.assert_not_called()


def test_missing_key_returns_service_unavailable(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hola"})
    assert response.status_code == 503


@pytest.mark.parametrize(
    "error,status",
    [
        (APIConnectionError(request=httpx.Request("POST", "https://example.com")), 502),
        (APITimeoutError(request=httpx.Request("POST", "https://example.com")), 504),
        (
            RateLimitError(
                "private error",
                response=httpx.Response(
                    429, request=httpx.Request("POST", "https://example.com")
                ),
                body=None,
            ),
            503,
        ),
    ],
)
def test_provider_errors_are_sanitized(client, model, error, status):
    model.ainvoke.side_effect = error
    response = client.post("/chat", json={"message": "Hola"})
    assert response.status_code == status
    assert "private error" not in response.text


def test_no_history_is_shared(client, model):
    client.post("/chat", json={"message": "Primero"})
    client.post("/chat", json={"message": "Segundo"})
    assert len(model.ainvoke.call_args.args[0]) == 2
    assert model.ainvoke.call_args.args[0][1].content == "Segundo"


def test_empty_model_output_returns_bad_gateway(client, model):
    model.ainvoke.return_value = AIMessage(content="")
    assert client.post("/chat", json={"message": "Hola"}).status_code == 502


def test_langchain_openai_round_trip_without_network(monkeypatch):
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "id": "resp_test",
                "object": "response",
                "created_at": 0,
                "status": "completed",
                "model": DEFAULT_MODEL,
                "output": [
                    {
                        "id": "msg_test",
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [
                            {"type": "output_text", "text": "¡Hola!", "annotations": []}
                        ],
                    }
                ],
            },
        )

    monkeypatch.setenv("OPENAI_API_KEY", "test-only-not-a-real-key")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            monkeypatch.setattr(
                "agent.chat.ChatOpenAI", partial(ChatOpenAI, http_async_client=client)
            )
            return await create_agent().reply("Hola")

    assert asyncio.run(run()) == "¡Hola!"
    assert requests[0].url.path.endswith("/responses")
    payload = json.loads(requests[0].content)
    assert payload["model"] == DEFAULT_MODEL
    assert payload["store"] is False
    assert payload["reasoning"]["effort"] == "none"
    assert payload["max_output_tokens"] == 1024
    assert payload["input"][-1]["content"] == "Hola"
