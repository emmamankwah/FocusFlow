import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

# Backend/.env (parents: chatbot -> ai -> app -> Backend).
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful AI assistant. Answer clearly and concisely."
)

CONTEXT_SYSTEM_PROMPT = (
    "You are a helpful AI assistant that answers questions based only on the "
    "provided context. If the answer is not in the context, say that you do not "
    "know and suggest the user consult a human expert.\n\n"
    "Context:\n{context}"
)


def build_system_prompt(context: str | None) -> str:
    if context:
        return CONTEXT_SYSTEM_PROMPT.format(context=context)
    return DEFAULT_SYSTEM_PROMPT


def get_llm_messages(messages, context: str | None = None) -> list[ChatCompletionMessageParam]:
    llm_messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": build_system_prompt(context)}
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


def get_reply(messages, context: str | None = None) -> str:
    completion = get_client().chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free"),
        messages=get_llm_messages(messages, context),
        temperature=0.7,
    )
    return completion.choices[0].message.content
