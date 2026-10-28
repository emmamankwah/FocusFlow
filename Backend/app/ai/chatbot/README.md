# AI Chatbot

FastAPI-based AI chatbot backend. Optionally grounds LLM answers in a
document context (e.g. the extracted boilerplate text from `model/file.py`).

## Setup

```bash
pip install -r chatbot/requirements.txt
cp chatbot/.env.example chatbot/.env   # then add your OPENAI_API_KEY
```

## Run

```bash
uvicorn chatbot.app:app --reload --port 8000
```

## Endpoints

### `GET /health`

Returns `{"status": "ok"}`.

### `POST /chat`

Request body:

```json
{
  "messages": [
    { "role": "user", "content": "What are the termination terms?" }
  ],
  "context": "Paste extracted document text here (optional)."
}
```

Response:

```json
{
  "reply": "The assistant's answer..."
}
```

- `messages` (required): conversation history in order (system/user/assistant).
- `context` (optional): document text the assistant should answer from.
  Without it, the assistant uses a generic default prompt.

## Configuration

- `OPENAI_API_KEY` — your OpenRouter API key (free tier, no card/phone; get one at openrouter.ai/keys).
- `OPENAI_MODEL` — free OpenRouter model (currently set to `nvidia/nemotron-3-ultra-550b-a55b:free`).
- `OPENAI_BASE_URL` — OpenAI-compatible base URL for OpenRouter:
  `https://openrouter.ai/api/v1`.

When using AgentRouter, point the client at your gateway, e.g.:

```
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://your-agentrouter.com/v1
OPENAI_MODEL=your-model-name
```

