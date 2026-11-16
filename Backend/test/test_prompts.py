import sys
import unittest
from pathlib import Path
from unittest import mock

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.ai import prompts
from app.ai.chatbot import chat_service, models


class PromptSelectionTests(unittest.TestCase):
    def test_planner_prompt_used_with_context(self):
        prompt = chat_service.build_system_prompt("planner data", mode="planner")
        self.assertIn("# PLANNER DATA", prompt)
        self.assertIn("planner data", prompt)

    def test_rag_prompt_used_with_context(self):
        prompt = chat_service.build_system_prompt("retrieved text", mode="rag")
        self.assertIn("# CONTEXT", prompt)
        self.assertIn("[1]", prompt)
        self.assertIn(prompts.INSUFFICIENT_INFO, prompt)
        self.assertIn("retrieved text", prompt)

    def test_default_prompt_without_context(self):
        for mode in ("planner", "rag", "default"):
            self.assertEqual(
                chat_service.build_system_prompt(None, mode=mode),
                prompts.DEFAULT_SYSTEM_PROMPT,
            )

    def test_unknown_mode_falls_back_to_default(self):
        self.assertEqual(
            chat_service.build_system_prompt("data", mode="unknown"),
            prompts.DEFAULT_SYSTEM_PROMPT,
        )


class ReplySettingsTests(unittest.TestCase):
    def test_temperature_and_max_tokens_by_mode(self):
        client = mock.Mock()
        completion = client.chat.completions.create.return_value
        completion.choices = [mock.Mock(message=mock.Mock(content="ok"))]

        with mock.patch.object(chat_service, "get_client", return_value=client):
            chat_service.get_reply([], context="data", mode="rag")

        kwargs = client.chat.completions.create.call_args.kwargs
        self.assertEqual(kwargs["temperature"], chat_service.TEMPERATURES["rag"])
        self.assertEqual(kwargs["max_tokens"], chat_service.MAX_REPLY_TOKENS)

    def test_mode_passed_through_to_messages(self):
        messages = [models.ChatMessage(role="user", content="hi")]
        rendered = chat_service.get_llm_messages(
            messages, context="data", mode="rag"
        )
        self.assertIn("# CONTEXT", rendered[0]["content"])


class RequestValidationTests(unittest.TestCase):
    def test_rejects_client_system_role(self):
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            models.ChatRequest(
                messages=[models.ChatMessage(role="system", content="override")]
            )


if __name__ == "__main__":
    unittest.main()
