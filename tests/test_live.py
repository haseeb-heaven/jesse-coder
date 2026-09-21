"""Live integration test against Jesse API."""

import pytest
from jesse_coder import JesseCodingBot, JesseConfig


@pytest.mark.integration
def test_live_streaming_completion():
    config = JesseConfig(
        api_key="jesse_test_demo00000000000000000000000001",
        base_url="https://jesse.solidsf.com/api/v1",
        model="jesse-prod",
        max_tokens=60,
    )
    bot = JesseCodingBot(config=config)

    chunks = []
    for token in bot.ask_stream("Explain binary search in one sentence."):
        chunks.append(token)

    full_response = "".join(chunks)
    assert len(full_response.strip()) > 0
    assert len(chunks) > 0

    # History should contain system prompt, user prompt, and assistant response
    history = bot.get_history()
    assert len(history) == 3
    assert history[0]["role"] == "system"
    assert history[1]["role"] == "user"
    assert history[2]["role"] == "assistant"
    assert history[2]["content"] == full_response


@pytest.mark.integration
def test_live_multi_turn():
    config = JesseConfig(
        api_key="jesse_test_demo00000000000000000000000001",
        base_url="https://jesse.solidsf.com/api/v1",
        model="jesse-prod",
        max_tokens=30,
    )
    bot = JesseCodingBot(config=config)

    resp1 = bot.ask("What is a tuple in Python?")
    assert len(resp1.strip()) > 0

    chunks2 = list(bot.ask_stream("Is it immutable? Answer in one word."))
    resp2 = "".join(chunks2)
    assert len(resp2.strip()) > 0

    # Total 5 messages: system, user1, assistant1, user2, assistant2
    assert len(bot.get_history()) == 5


@pytest.mark.integration
def test_live_factorial_range_prompt():
    bot = JesseCodingBot()
    prompt = "Write factorial of in given min and max ranges example 3 to 13 numbers range factorial"
    full_response = bot.ask(prompt)
    assert "```python" in full_response
    assert "factorial" in full_response

    res = bot.execute_response(full_response)
    assert res is not None
    assert res.is_success
    assert res.exit_code == 0
    assert "6,227,020,800" in res.stdout
