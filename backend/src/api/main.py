import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from openai import APIError, APITimeoutError, RateLimitError
from pydantic import BaseModel, StringConstraints

from agent.chat import ChatAgent, create_agent

app = FastAPI(title="DevAtlas", version="0.1.0")


class ChatRequest(BaseModel):
    message: Annotated[
        str,
        StringConstraints(
            strict=True, strip_whitespace=True, min_length=1, max_length=8000
        ),
    ]


class ChatResponse(BaseModel):
    reply: str


def get_agent() -> ChatAgent:
    if not os.getenv("OPENAI_API_KEY", "").strip():
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")
    return create_agent()


@app.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest, agent: Annotated[ChatAgent, Depends(get_agent)]
) -> ChatResponse:
    try:
        reply = await agent.reply(body.message)
    except APITimeoutError as exc:
        raise HTTPException(504, "Model request timed out") from exc
    except RateLimitError as exc:
        raise HTTPException(503, "Model service is temporarily unavailable") from exc
    except (APIError, ValueError) as exc:
        raise HTTPException(502, "Model service could not produce a response") from exc
    return ChatResponse(reply=reply)
