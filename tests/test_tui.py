import asyncio
from jesse_coder.tui import JesseTUIApp
from jesse_coder.bot import JesseCodingBot


def test_tui_widget_composition():
    async def _run():
        bot = JesseCodingBot()
        app = JesseTUIApp(bot=bot)

        async with app.run_test() as pilot:
            assert app.query_one("#chat-markdown") is not None
            assert app.query_one("#chat-raw") is not None
            assert app.query_one("#btn-toggle-raw") is not None
            assert app.query_one("#code-markdown") is not None
            assert app.query_one("#btn-run") is not None
            assert app.query_one("#btn-auto-run") is not None
            assert app.query_one("#btn-copy") is not None
            assert app.query_one("#btn-clear") is not None
            assert app.query_one("#lang-select") is not None
            assert app.query_one("#console-output") is not None
            assert app.query_one("#chat-input") is not None
            assert app.query_one("#btn-send") is not None

    asyncio.run(_run())


def test_tui_actions():
    async def _run():
        bot = JesseCodingBot()
        app = JesseTUIApp(bot=bot)

        async with app.run_test() as pilot:
            # Test auto-run toggle
            assert app.auto_run
            app.action_toggle_auto_run()
            assert not app.auto_run
            app.action_toggle_auto_run()
            assert app.auto_run

            # Test raw toggle
            assert not app.show_raw
            app.action_toggle_raw()
            assert app.show_raw
            assert app.query_one("#chat-raw").display
            assert not app.query_one("#chat-markdown").display
            app.action_toggle_raw()
            assert not app.show_raw

            # Set code manually and run
            app.current_code = "print('TUI test passed')"
            app.current_language = "python"
            app._update_code_display()

            # Trigger run code
            app.action_run_code()
            await pilot.pause(0.3)

            # Trigger copy code
            app.action_copy_code()

            # Trigger clear
            app.action_clear_all()
            assert app.current_code == ""

    asyncio.run(_run())


def test_tui_execution_display_and_stream():
    async def _run():
        bot = JesseCodingBot()
        app = JesseTUIApp(bot=bot)

        async with app.run_test() as pilot:
            # Simulate a full turn with code
            fake_response = (
                "Here is the solution:\n\n"
                "```python\n"
                "print('EXECUTION_VERIFIED_OUTPUT_1234')\n"
                "```"
            )
            app._finalize_turn("dummy prompt", fake_response)
            assert app.current_code.strip() == "print('EXECUTION_VERIFIED_OUTPUT_1234')"

            # Wait for background worker execution
            await pilot.pause(0.5)

            # Check console output
            console_text = str(app.query_one("#console-output").render())
            assert "EXECUTION_VERIFIED_OUTPUT_1234" in console_text
            assert "SUCCESS" in console_text

            # Check that it also rendered into dialogue turn
            last_turn = app.dialogue_history[-1]["content"]
            assert "EXECUTION_VERIFIED_OUTPUT_1234" in last_turn

    asyncio.run(_run())
