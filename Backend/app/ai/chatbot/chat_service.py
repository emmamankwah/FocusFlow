import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.ai.prompts import (
    DEFAULT_SYSTEM_PROMPT,
    planner_system_prompt,
    rag_system_prompt,
)

# Backend/.env (parents: chatbot -> ai -> app -> Backend).
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

TEMPERATURES = {
    "planner": 0.3,
    "rag": 0.2,
    "default": 0.7,
}
MAX_REPLY_TOKENS = 450


def normalise_mode(mode: str) -> str:
    return mode if mode in TEMPERATURES else "default"


def build_system_prompt(context: str | None, mode: str = "planner") -> str:
    mode = normalise_mode(mode)
    if mode == "rag" and context:
        return rag_system_prompt(context)
    if mode == "planner" and context:
        return planner_system_prompt(context)
    return DEFAULT_SYSTEM_PROMPT


def get_llm_messages(
    messages,
    context: str | None = None,
    mode: str = "planner",
) -> list[ChatCompletionMessageParam]:
    llm_messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": build_system_prompt(context, mode)}
    ]
    for message in messages:
        llm_messages.append({"role": message.role, "content": message.content})
    return llm_messages


def get_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL"),
        timeout=60.0,
    )


def get_reply(messages, context: str | None = None, mode: str = "planner") -> str:
    mode = normalise_mode(mode)
    completion = get_client().chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free"),
        messages=get_llm_messages(messages, context, mode),
        temperature=TEMPERATURES[mode],
        max_tokens=MAX_REPLY_TOKENS,
    )
    return completion.choices[0].message.content
