"""
Conversation management module for Jesse Coding Bot.
Handles chat history, system prompt maintenance, message serialization, and windowed context.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ChatMessage:
    """Represents a single message in the conversation."""

    role: str
    content: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, str]:
        """Format as OpenAI message dictionary."""
        return {"role": self.role, "content": self.content}

    def to_full_dict(self) -> Dict[str, Any]:
        """Format with metadata for export/logging."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
        }


class ConversationManager:
    """
    Manages multi-turn conversation history for the coding chatbot.
    Preserves system instructions while sliding windowing older turns if necessary.
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        max_turns: int = 20,
    ) -> None:
        self.max_turns = max_turns
        self.system_prompt: Optional[str] = system_prompt
        self.messages: List[ChatMessage] = []

        if system_prompt:
            self.messages.append(ChatMessage(role="system", content=system_prompt))

    def set_system_prompt(self, system_prompt: str) -> None:
        """Update or set the system prompt."""
        self.system_prompt = system_prompt
        if self.messages and self.messages[0].role == "system":
            self.messages[0].content = system_prompt
        else:
            self.messages.insert(0, ChatMessage(role="system", content=system_prompt))

    def add_user_message(self, content: str) -> ChatMessage:
        """Add a user message to history and enforce window limits."""
        msg = ChatMessage(role="user", content=content)
        self.messages.append(msg)
        self._enforce_window()
        return msg

    def add_assistant_message(self, content: str) -> ChatMessage:
        """Add an assistant response to history and enforce window limits."""
        msg = ChatMessage(role="assistant", content=content)
        self.messages.append(msg)
        self._enforce_window()
        return msg

    def pop_last(self) -> Optional[ChatMessage]:
        """
        Remove the most recent message (useful for rolling back uncommitted turns on error).
        """
        if self.messages and self.messages[-1].role != "system":
            return self.messages.pop()
        return None

    def get_messages(self) -> List[Dict[str, str]]:
        """Return history serialized for OpenAI chat completions."""
        return [msg.to_dict() for msg in self.messages]

    def clear(self) -> None:
        """Clear all conversation turns, preserving the system prompt."""
        self.messages.clear()
        if self.system_prompt:
            self.messages.append(
                ChatMessage(role="system", content=self.system_prompt)
            )

    def _enforce_window(self) -> None:
        """
        Keep conversation length within max_turns pairs, preserving the system message.
        """
        has_system = self.messages and self.messages[0].role == "system"
        dialogue = self.messages[1:] if has_system else self.messages

        # max_turns represents turn pairs (user + assistant)
        max_msgs = self.max_turns * 2
        if len(dialogue) > max_msgs:
            excess = len(dialogue) - max_msgs
            dialogue = dialogue[excess:]
            self.messages = ([self.messages[0]] if has_system else []) + dialogue

    def export_history(self) -> List[Dict[str, Any]]:
        """Export history with timestamps."""
        return [msg.to_full_dict() for msg in self.messages]

    def import_history(self, raw_messages: List[Dict[str, Any]]) -> None:
        """Import history from list of dictionaries."""
        self.messages.clear()
        for m in raw_messages:
            self.messages.append(
                ChatMessage(
                    role=m.get("role", "user"),
                    content=m.get("content", ""),
                    timestamp=m.get("timestamp", time.time()),
                )
            )
        if self.messages and self.messages[0].role == "system":
            self.system_prompt = self.messages[0].content

    def __len__(self) -> int:
        return len(self.messages)
