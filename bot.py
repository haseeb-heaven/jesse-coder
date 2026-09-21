"""
JesseCodingBot Orchestrator Module.
General-purpose coding agent: sends prompts to Jesse API, streams responses,
extracts code, and executes it. No synthesis, no hardcoding.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, List, Optional, Tuple

try:
    from .client import JesseClient
    from .config import JesseConfig
    from .conversation import ConversationManager
    from .exceptions import JesseBotError
    from .executor import CodeExecutor, ExecutionResult
    from .code_extractor import (
        ExtractedCodeBlock,
        extract_code_blocks,
        get_primary_code_block,
    )
except ImportError:
    from client import JesseClient
    from config import JesseConfig
    from conversation import ConversationManager
    from exceptions import JesseBotError
    from executor import CodeExecutor, ExecutionResult
    from code_extractor import (
        ExtractedCodeBlock,
        extract_code_blocks,
        get_primary_code_block,
    )

logger = logging.getLogger("jesse_coder.bot")


class JesseCodingBot:
    """
    General-purpose coding agent.
    Sends prompts to the Jesse API, streams responses, extracts code blocks,
    and executes them in an isolated subprocess.
    """

    def __init__(
        self,
        config: Optional[JesseConfig] = None,
        client: Optional[JesseClient] = None,
        conversation: Optional[ConversationManager] = None,
        executor: Optional[CodeExecutor] = None,
    ) -> None:
        self.config = config or JesseConfig()
        self.config.validate()

        self.client = client or JesseClient(config=self.config)
        self.conversation = conversation or ConversationManager(
            system_prompt=self.config.system_prompt,
            max_turns=self.config.max_history_turns,
        )
        self.executor = executor or CodeExecutor()

        self.last_raw_api_response: Optional[str] = None
        self.last_assistant_response: Optional[str] = None
        self.last_extracted_code: Optional[ExtractedCodeBlock] = None
        self.last_execution_result: Optional[ExecutionResult] = None

    def _prepare_prompt_with_context(self, user_prompt: str) -> str:
        """
        If this is a follow-up turn and we have active code from a previous turn,
        ensure the model sees the active working code so it can accurately fulfill
        the follow-up request rather than losing context.
        """
        if (
            self.last_extracted_code
            and "```" not in user_prompt
            and len(self.conversation.messages) > 1
        ):
            lang = self.last_extracted_code.language or "python"
            code_str = self.last_extracted_code.code.strip()
            if code_str:
                return (
                    f"Existing Working Code:\n"
                    f"```{lang}\n{code_str}\n```\n\n"
                    f"User Follow-up Request:\n{user_prompt}\n\n"
                    f"Please provide the complete, updated code in ```{lang} ... ```."
                )
        return user_prompt

    def ask_stream(
        self,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **extra_params: Any,
    ) -> Iterator[str]:
        """
        Send a prompt to the Jesse API and yield streaming token chunks.
        Whatever the API returns is streamed verbatim — no interception.
        """
        if not user_prompt or not user_prompt.strip():
            return

        outgoing_prompt = self._prepare_prompt_with_context(user_prompt)
        self.conversation.add_user_message(outgoing_prompt)
        accumulated: List[str] = []

        try:
            messages = self.conversation.get_messages()
            for token in self.client.stream_chat(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **extra_params,
            ):
                accumulated.append(token)
                yield token

            full_text = "".join(accumulated)
            self.last_raw_api_response = full_text

            if full_text.strip():
                self.conversation.add_assistant_message(full_text)
                self.last_assistant_response = full_text
                extracted = get_primary_code_block(full_text)
                if extracted:
                    self.last_extracted_code = extracted
            else:
                self.conversation.pop_last()

        except Exception as e:
            self.conversation.pop_last()
            if isinstance(e, JesseBotError):
                raise
            raise JesseBotError(f"Streaming failed: {e}", original_error=e) from e

    def ask(
        self,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **extra_params: Any,
    ) -> str:
        """
        Send a prompt and return the full response synchronously.
        """
        if not user_prompt or not user_prompt.strip():
            return ""

        outgoing_prompt = self._prepare_prompt_with_context(user_prompt)
        self.conversation.add_user_message(outgoing_prompt)
        try:
            messages = self.conversation.get_messages()
            response = self.client.chat(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **extra_params,
            )
            self.last_raw_api_response = response
            self.conversation.add_assistant_message(response)
            self.last_assistant_response = response
            extracted = get_primary_code_block(response)
            if extracted:
                self.last_extracted_code = extracted
            return response
        except Exception:
            self.conversation.pop_last()
            raise

    def execute_code(
        self,
        code: str,
        language: str = "python",
        cwd: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> ExecutionResult:
        """Execute code in an isolated subprocess."""
        result = self.executor.execute_code(
            code=code,
            language=language,
            cwd=cwd,
            timeout=timeout,
        )
        self.last_execution_result = result
        return result

    def execute_response(
        self,
        response_text: Optional[str] = None,
        preferred_lang: Optional[str] = None,
        cwd: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Optional[ExecutionResult]:
        """Extract code from the response and execute it."""
        target = response_text or self.last_assistant_response
        if not target:
            return None

        code_block = get_primary_code_block(target, preferred_lang=preferred_lang)
        if not code_block:
            return None

        self.last_extracted_code = code_block
        return self.execute_code(
            code=code_block.code,
            language=code_block.language,
            cwd=cwd,
            timeout=timeout,
        )

    def ask_and_execute(
        self,
        user_prompt: str,
        preferred_lang: Optional[str] = None,
        cwd: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Tuple[str, Optional[ExecutionResult]]:
        """Ask a question, receive response, extract and execute the code."""
        response = self.ask(user_prompt)
        result = self.execute_response(
            response_text=response,
            preferred_lang=preferred_lang,
            cwd=cwd,
            timeout=timeout,
        )
        return response, result

    def reset_conversation(self) -> None:
        """Reset conversation history."""
        self.conversation.clear()
        self.last_raw_api_response = None
        self.last_assistant_response = None
        self.last_extracted_code = None
        self.last_execution_result = None

    def set_system_prompt(self, prompt: str) -> None:
        """Update the system prompt."""
        self.config.system_prompt = prompt
        self.conversation.set_system_prompt(prompt)

    def switch_model(self, model_name: str) -> None:
        """Switch the active model."""
        self.config.model = model_name

    def get_history(self) -> List[Dict[str, str]]:
        """Return the current conversation messages."""
        return self.conversation.get_messages()

    def close(self) -> None:
        """Release network connections."""
        self.client.close()

    def __enter__(self) -> JesseCodingBot:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
