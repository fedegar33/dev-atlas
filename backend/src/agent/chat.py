import os

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from agent.prompts import SYSTEM_PROMPT

DEFAULT_MODEL = "gpt-5.6-terra"


class ChatAgent:
    """Single-turn agent; no tools, memory, or retrieval yet."""

    def __init__(self, model: BaseChatModel) -> None:
        self.model = model

    async def reply(self, message: str) -> str:
        response = await self.model.ainvoke(
            [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=message)]
        )
        text = response.text.strip()
        if not text:
            raise ValueError("Model returned no text")
        return text


def create_agent() -> ChatAgent:
    return ChatAgent(
        ChatOpenAI(
            model=os.getenv("OPENAI_MODEL") or DEFAULT_MODEL,
            use_responses_api=True,
            reasoning_effort="none",
            max_tokens=1024,
            timeout=30,
            max_retries=0,
            store=False,
        )
    )
