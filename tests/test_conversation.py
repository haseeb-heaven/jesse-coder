"""Tests for ConversationManager and ChatMessage."""

import pytest
from jesse_coder.conversation import ConversationManager, ChatMessage


def test_conversation_initialization():
    sys_prompt = "You are a Python coding bot."
    conv = ConversationManager(system_prompt=sys_prompt)

    messages = conv.get_messages()
    assert len(messages) == 1
    assert messages[0] == {"role": "system", "content": sys_prompt}


def test_conversation_turns():
    conv = ConversationManager(system_prompt="System prompt")
    conv.add_user_message("Write a sort function")
    conv.add_assistant_message("def sort_list(lst): return sorted(lst)")

    msgs = conv.get_messages()
    assert len(msgs) == 3
    assert msgs[1]["role"] == "user"
    assert msgs[1]["content"] == "Write a sort function"
    assert msgs[2]["role"] == "assistant"
    assert "def sort_list" in msgs[2]["content"]


def test_conversation_windowing():
    # Limit max turns to 2 pairs (4 dialogue messages max + 1 system)
    conv = ConversationManager(system_prompt="System", max_turns=2)
    for i in range(5):
        conv.add_user_message(f"User {i}")
        conv.add_assistant_message(f"Bot {i}")

    msgs = conv.get_messages()
    assert msgs[0]["role"] == "system"
    # Total messages: 1 system + 4 dialogue messages
    assert len(msgs) == 5
    assert msgs[1]["content"] == "User 3"
    assert msgs[2]["content"] == "Bot 3"
    assert msgs[3]["content"] == "User 4"
    assert msgs[4]["content"] == "Bot 4"


def test_conversation_clear():
    conv = ConversationManager(system_prompt="Preserved System")
    conv.add_user_message("Hello")
    conv.add_assistant_message("Hi")
    assert len(conv) == 3

    conv.clear()
    assert len(conv) == 1
    msgs = conv.get_messages()
    assert msgs[0]["content"] == "Preserved System"


def test_pop_last():
    conv = ConversationManager(system_prompt="System")
    conv.add_user_message("Failed query")
    assert len(conv) == 2

    popped = conv.pop_last()
    assert popped is not None
    assert popped.content == "Failed query"
    assert len(conv) == 1
    assert conv.pop_last() is None  # Should not pop system message


def test_export_and_import():
    conv = ConversationManager(system_prompt="System A")
    conv.add_user_message("Q1")
    conv.add_assistant_message("A1")

    exported = conv.export_history()
    assert len(exported) == 3

    new_conv = ConversationManager()
    new_conv.import_history(exported)
    assert new_conv.system_prompt == "System A"
    assert len(new_conv) == 3
