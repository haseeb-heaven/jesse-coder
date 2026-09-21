"""
Jesse-Coder - Modern Royal Blue Terminal User Interface (TUI).
Built with Textual & Rich.
Features:
- Pure Deep Blue & Royal Blue color scheme (no pink/turquoise)
- Prominently docked Chat Input Box with immediate Enter-to-send
- Real-time token streaming in the conversation window
- Dedicated Extracted Code Workbench showing isolated code
- One-click [▶ Run Code] and [📋 Copy Code] buttons
- Live Open-Agent execution console
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import List, Optional

import pyperclip
from textual import events, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    LoadingIndicator,
    Markdown,
    Select,
    Static,
)

# Ensure parent and module are importable
package_root = str(Path(__file__).resolve().parent.parent)
if package_root not in sys.path:
    sys.path.insert(0, package_root)

try:
    from .bot import JesseCodingBot
    from .code_extractor import ExtractedCodeBlock, get_primary_code_block
    from .config import JesseConfig
    from .exceptions import JesseBotError
    from .executor import CodeExecutor, ExecutionResult
except (ImportError, ValueError):
    from bot import JesseCodingBot
    from code_extractor import ExtractedCodeBlock, get_primary_code_block
    from config import JesseConfig
    from exceptions import JesseBotError
    from executor import CodeExecutor, ExecutionResult

logger = logging.getLogger("jesse_coder.tui")


class ScrollPane(VerticalScroll):
    """Smooth scrollable container."""

    def on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        self.scroll_relative(y=max(3, abs(event.delta_y) * 3), immediate=True)
        event.stop()

    def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        self.scroll_relative(y=-max(3, abs(event.delta_y) * 3), immediate=True)
        event.stop()


SUPPORTED_LANGUAGES = [
    ("Python", "python"),
    ("Bash / Shell", "bash"),
    ("JavaScript / Node", "javascript"),
    ("Rust", "rust"),
    ("C++", "cpp"),
    ("Plain Text", "text"),
]


class JesseTUIApp(App[None]):
    """
    Polished Royal Blue Textual application for Jesse-Coder.
    """

    TITLE = "Jesse-Coder"
    SUB_TITLE = "Autonomous Engineering Assistant · Code Execution Engine"
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+e", "run_code", "Run Code"),
        Binding("ctrl+a", "toggle_auto_run", "Toggle Auto-Run"),
        Binding("ctrl+y", "copy_code", "Copy Code"),
        Binding("ctrl+t", "toggle_raw", "Toggle Raw"),
        Binding("ctrl+l", "clear_all", "Clear"),
        Binding("ctrl+r", "focus_input", "Focus Prompt"),
    ]

    CSS = """
    Screen {
        background: #080b12;
        color: #e6edf7;
    }
    Header {
        background: #111827;
        color: #f8fafc;
    }
    #top-bar {
        height: 1;
        background: #111827;
        color: #8da2c0;
        padding: 0 1;
    }
    .badge {
        margin-right: 2;
        text-style: bold;
        color: #8da2c0;
    }
    #status-badge {
        color: #71d7ff;
    }
    #main-body {
        height: 1fr;
        padding: 0 1;
        margin-top: 1;
    }
    .pane {
        border: round #26344d;
        background: #0d1320;
        padding: 1 1;
    }
    #chat-pane {
        width: 1fr;
        margin-right: 1;
    }
    #workbench-pane {
        width: 1fr;
    }
    #chat-header {
        height: 3;
        align: left middle;
        margin-bottom: 0;
    }
    .pane-title {
        height: 1;
        color: #71d7ff;
        text-style: bold;
        margin-bottom: 0;
    }
    #btn-toggle-raw {
        width: 14;
        height: 3;
        background: #162033;
        border: tall #26344d;
        color: #71d7ff;
        margin-left: 2;
    }
    #btn-toggle-raw:hover {
        background: #26344d;
        color: #f8fafc;
    }
    #btn-toggle-raw.-active {
        background: #0891b2;
        color: #ffffff;
        border: none;
    }
    #chat-raw {
        display: none;
        color: #71d7ff;
    }
    .sub-title {
        height: 1;
        color: #8da2c0;
        text-style: bold;
        margin-top: 1;
        margin-bottom: 0;
    }
    ScrollPane {
        overflow-y: scroll;
        scrollbar-size-vertical: 2;
        scrollbar-color: #22d3ee;
        scrollbar-color-hover: #67e8f9;
        scrollbar-color-active: #a78bfa;
    }
    #chat-scroll {
        height: 1fr;
        background: #080b12;
        border: solid #26344d;
        padding: 0 1;
    }
    #input-dock {
        height: 4;
        dock: bottom;
        padding-top: 1;
        align: left middle;
        background: #0d1320;
    }
    #chat-input {
        width: 1fr;
        height: 3;
        border: tall #344766;
        background: #111827;
        color: #e6edf7;
        padding: 0 1;
    }
    #chat-input:focus {
        border: tall #22d3ee;
        background: #0d1320;
    }
    #btn-send {
        width: 12;
        height: 3;
        margin-left: 1;
        background: #0891b2;
        color: #ffffff;
        text-style: bold;
        border: none;
    }
    #btn-send:hover {
        background: #06b6d4;
    }
    #workbench-controls {
        height: 3;
        align: left middle;
        margin-bottom: 1;
    }
    #lang-select {
        width: 18;
        height: 3;
        margin-right: 1;
        background: #111827;
        border: tall #344766;
        color: #e6edf7;
    }
    #lang-select:focus {
        border: tall #22d3ee;
    }
    #btn-run {
        width: 13;
        height: 3;
        margin-right: 1;
        background: #0891b2;
        color: #ffffff;
        text-style: bold;
        border: none;
    }
    #btn-run:hover {
        background: #06b6d4;
    }
    #btn-auto-run {
        width: 14;
        height: 3;
        margin-right: 1;
        background: #0891b2;
        color: #ffffff;
        text-style: bold;
        border: none;
    }
    #btn-auto-run.-off {
        background: #162033;
        color: #8da2c0;
        border: tall #26344d;
    }
    #btn-copy {
        width: 13;
        height: 3;
        margin-right: 1;
        background: #162033;
        border: tall #26344d;
        color: #71d7ff;
        text-style: bold;
    }
    #btn-copy:hover {
        background: #26344d;
        color: #f8fafc;
    }
    #btn-clear {
        width: 10;
        height: 3;
        background: #162033;
        color: #8da2c0;
        border: none;
    }
    #btn-clear:hover {
        background: #26344d;
        color: #e6edf7;
    }
    #code-scroll {
        height: 1fr;
        min-height: 7;
        background: #080b12;
        border: solid #26344d;
        padding: 0 1;
    }
    #console-scroll {
        height: 1fr;
        min-height: 8;
        background: #05080e;
        border: solid #0891b2;
        padding: 0 1;
        margin-top: 0;
    }
    #console-output {
        color: #71d7ff;
    }
    Footer {
        background: #0d1320;
        color: #8da2c0;
    }
    """

    def __init__(self, bot: Optional[JesseCodingBot] = None) -> None:
        super().__init__()
        self.bot: JesseCodingBot = bot or JesseCodingBot()
        self.current_code: str = ""
        self.current_language: str = "python"
        self.dialogue_history: List[dict[str, str]] = []
        self.show_raw: bool = False
        self.auto_run: bool = True

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="top-bar"):
            yield Static(f"🔷 Model: {self.bot.config.model}", classes="badge")
            yield Static(f"🌐 Host: {self.bot.config.base_url}", classes="badge")
            yield Static("⚡ Status: Ready", id="status-badge", classes="badge")

        with Horizontal(id="main-body"):
            # LEFT COLUMN: Conversation & Prominent Input Box
            with Vertical(id="chat-pane", classes="pane"):
                with Horizontal(id="chat-header"):
                    yield Static("💬 CONVERSATION STREAM", classes="pane-title")
                    yield Button("📄 Raw: OFF", id="btn-toggle-raw")

                with ScrollPane(id="chat-scroll"):
                    yield Markdown(
                        "*Type a prompt below to generate code, explain concepts, or debug.*",
                        id="chat-markdown",
                    )
                    yield Static(
                        "*No raw response yet.*",
                        id="chat-raw",
                    )

                with Horizontal(id="input-dock"):
                    yield Input(
                        placeholder="Enter your prompt here… (e.g. Write a python script to test network latency)",
                        id="chat-input",
                    )
                    yield Button("Send ↵", id="btn-send")

            # RIGHT COLUMN: Extracted Code Workbench & Execution
            with Vertical(id="workbench-pane", classes="pane"):
                yield Static("🛠️ CODE WORKBENCH & EXECUTION", classes="pane-title")

                with Horizontal(id="workbench-controls"):
                    yield Select(
                        SUPPORTED_LANGUAGES,
                        value="python",
                        allow_blank=False,
                        id="lang-select",
                    )
                    yield Button("▶ Run Code", id="btn-run")
                    yield Button("⚡ Auto: ON", id="btn-auto-run")
                    yield Button("📋 Copy Code", id="btn-copy")
                    yield Button("🧹 Clear", id="btn-clear")

                yield Static("📝 Extracted Code Preview", classes="sub-title")
                with ScrollPane(id="code-scroll"):
                    yield Markdown(
                        "```python\n# Extracted code will appear here after Jesse responds\n```",
                        id="code-markdown",
                    )

                yield Static("📟 Execution Console (open-agent engine)", classes="sub-title")
                with ScrollPane(id="console-scroll"):
                    yield Static("Ready. Click [▶ Run Code] to execute.", id="console-output")

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#chat-input", Input).focus()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "lang-select" and event.value:
            self.current_language = str(event.value)
            self._update_code_display()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-send":
            self._submit_query()
        elif event.button.id == "btn-toggle-raw":
            self.action_toggle_raw()
        elif event.button.id == "btn-run":
            self.action_run_code()
        elif event.button.id == "btn-auto-run":
            self.action_toggle_auto_run()
        elif event.button.id == "btn-copy":
            self.action_copy_code()
        elif event.button.id == "btn-clear":
            self.action_clear_all()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._submit_query()

    def action_toggle_auto_run(self) -> None:
        """Toggle automatic code execution upon generation."""
        self.auto_run = not self.auto_run
        btn = self.query_one("#btn-auto-run", Button)
        if self.auto_run:
            btn.label = "⚡ Auto: ON"
            btn.remove_class("-off")
            self.notify("Auto-execution ENABLED: code runs immediately on generation", severity="information")
        else:
            btn.label = "⚡ Auto: OFF"
            btn.add_class("-off")
            self.notify("Auto-execution DISABLED: click [▶ Run Code] to execute", severity="information")

    def action_toggle_raw(self) -> None:
        """Toggle between formatted markdown and raw response view."""
        self.show_raw = not self.show_raw
        md_view = self.query_one("#chat-markdown", Markdown)
        raw_view = self.query_one("#chat-raw", Static)
        btn = self.query_one("#btn-toggle-raw", Button)

        if self.show_raw:
            md_view.display = False
            raw_view.display = True
            btn.label = "📄 Raw: ON"
            btn.add_class("-active")
            self._update_raw_display()
            self.notify("RAW response mode ON (verbatim model stream)", severity="information")
        else:
            raw_view.display = False
            md_view.display = True
            btn.label = "📄 Raw: OFF"
            btn.remove_class("-active")
            self._render_conversation()
            self.notify("Formatted Markdown view ON", severity="information")

    def _submit_query(self) -> None:
        input_widget = self.query_one("#chat-input", Input)
        query = input_widget.value.strip()
        if not query:
            return

        input_widget.value = ""
        input_widget.disabled = True
        self.query_one("#btn-send", Button).disabled = True
        self.query_one("#status-badge", Static).update("⚡ Status: Streaming…")

        self.stream_response_worker(query)

    @work(thread=True, exclusive=True)
    def stream_response_worker(self, prompt: str) -> None:
        accumulated: List[str] = []
        self.call_from_thread(self._append_user_message, prompt)

        try:
            for token in self.bot.ask_stream(prompt):
                accumulated.append(token)
                partial = "".join(accumulated)
                self.call_from_thread(self._update_assistant_stream, partial)

            full_text = "".join(accumulated)
            self.call_from_thread(self._finalize_turn, prompt, full_text)

        except Exception as e:
            logger.exception("Streaming error")
            self.call_from_thread(self._handle_error, str(e))

    def _append_user_message(self, prompt: str) -> None:
        self.dialogue_history.append({"role": "user", "content": prompt})
        self._render_conversation(in_progress="*Jesse is generating code…*")
        self._update_raw_display(in_progress="[Awaiting stream...]")

    def _update_assistant_stream(self, partial_text: str) -> None:
        if self.show_raw:
            self._update_raw_display(in_progress=partial_text)
        else:
            self._render_conversation(in_progress=partial_text)
        self.query_one("#chat-scroll", ScrollPane).scroll_end(animate=False)

    def _finalize_turn(self, prompt: str, full_response: str) -> None:
        self.dialogue_history.append({"role": "assistant", "content": full_response})
        self._render_conversation()
        self._update_raw_display()

        # Extract code block
        block = get_primary_code_block(full_response, preferred_lang=self.current_language)
        if block:
            self.current_code = block.code
            self.current_language = block.language
            try:
                self.query_one("#lang-select", Select).value = self.current_language
            except Exception:
                pass
            self._update_code_display()
            self.notify(f"Extracted {block.language.upper()} code block ready to run!", severity="information")

            # Automatically run extracted code if auto_run is enabled
            if self.auto_run:
                self.action_run_code()

        self._finish_processing("⚡ Status: Ready")

    def _render_conversation(self, in_progress: Optional[str] = None) -> None:
        parts: List[str] = []
        for turn in self.dialogue_history:
            if turn["role"] == "user":
                parts.append(f"### 👤 User Prompt\n{turn['content']}")
            else:
                parts.append(f"### 🤖 Jesse Response\n{turn['content']}")

        if in_progress:
            parts.append(f"### 🤖 Jesse Response\n{in_progress}")

        content = "\n\n---\n\n".join(parts) if parts else "*Type a prompt below to begin.*"
        self.query_one("#chat-markdown", Markdown).update(content)

    def _update_raw_display(self, in_progress: Optional[str] = None) -> None:
        lines: List[str] = []

        if self.bot.last_raw_api_response:
            lines.append("=" * 22 + " [UPSTREAM JESSE API RAW OUTPUT] " + "=" * 22)
            lines.append(self.bot.last_raw_api_response.strip())
            lines.append("\n" + "=" * 20 + " [VERBATIM DIALOGUE TURNS] " + "=" * 20)

        for turn in self.dialogue_history:
            role = turn["role"].upper()
            lines.append(f"[{role}]:\n{turn['content']}\n")

        if in_progress:
            lines.append(f"[ASSISTANT (STREAMING RAW)]:\n{in_progress}\n")

        raw_content = "\n".join(lines) if lines else "*No raw messages yet.*"
        try:
            self.query_one("#chat-raw", Static).update(raw_content)
        except Exception:
            pass

    def _update_code_display(self) -> None:
        if not self.current_code.strip():
            display = f"```{self.current_language}\n# No code extracted from current turn\n```"
        else:
            display = f"```{self.current_language}\n{self.current_code}\n```"
        self.query_one("#code-markdown", Markdown).update(display)

    def _handle_error(self, error_msg: str) -> None:
        self.notify(error_msg, severity="error", timeout=8)
        self.query_one("#status-badge", Static).update(f"⚡ Status: Error")
        self._finish_processing("⚡ Status: Error")

    def _finish_processing(self, status_label: str) -> None:
        self.query_one("#status-badge", Static).update(status_label)
        self.query_one("#chat-input", Input).disabled = False
        self.query_one("#btn-send", Button).disabled = False
        self.query_one("#chat-input", Input).focus()

    def action_run_code(self) -> None:
        """Run currently displayed code in background worker via CodeExecutor."""
        code_to_run = self.current_code.strip()
        if not code_to_run:
            self.notify("No code to run! Type a prompt to generate code first.", severity="warning")
            return

        self.query_one("#status-badge", Static).update("⚡ Status: Executing code…")
        self.query_one("#console-output", Static).update("Executing in open-agent process engine…")

        self.execute_code_worker(code_to_run, self.current_language)

    @work(thread=True, exclusive=True)
    def execute_code_worker(self, code: str, language: str) -> None:
        try:
            res: ExecutionResult = self.bot.execute_code(code, language=language)
            self.call_from_thread(self._render_execution_result, res)
        except Exception as e:
            logger.exception("Execution error")
            self.call_from_thread(self._render_execution_failure, str(e))

    def _render_execution_result(self, res: ExecutionResult) -> None:
        status_tag = "SUCCESS" if res.is_success else ("TIMEOUT" if res.timed_out else "FAILED")
        header = f"[{res.language.upper()} · {status_tag} · Exit: {res.exit_code} · {res.duration_ms:.1f}ms]\n"

        lines = [header]
        if res.stdout:
            lines.append(res.stdout)
        if res.stderr:
            lines.append(f"[STDERR]:\n{res.stderr}")
        if res.error and not res.stderr:
            lines.append(f"[ERROR]: {res.error}")
        if not res.stdout and not res.stderr and not res.error:
            lines.append(f"[Finished with exit code {res.exit_code} and no output]")

        combined = "\n".join(lines)
        self.query_one("#console-output", Static).update(combined)
        self.query_one("#status-badge", Static).update(f"⚡ Status: Execution {status_tag}")
        self.query_one("#console-scroll", ScrollPane).scroll_end(animate=False)

        # ALSO render directly into conversation turn so user sees it in the chat stream!
        out_content = res.stdout.strip() or res.stderr.strip() or res.error or "(Process finished with no output)"
        exec_stream_entry = (
            f"\n\n---\n\n### 📟 Code Execution Output [{res.language.upper()} · {status_tag} · Exit {res.exit_code} · {res.duration_ms:.1f}ms]\n"
            f"```text\n{out_content}\n```"
        )
        if self.dialogue_history and self.dialogue_history[-1]["role"] == "assistant":
            if "### 📟 Code Execution Output" not in self.dialogue_history[-1]["content"]:
                self.dialogue_history[-1]["content"] += exec_stream_entry
                self._render_conversation()
                self._update_raw_display()

        sev = "information" if res.is_success else "error"
        self.notify(f"Execution {status_tag} ({res.duration_ms:.1f}ms)", severity=sev)

    def _render_execution_failure(self, error: str) -> None:
        self.query_one("#console-output", Static).update(f"[Execution Crash]: {error}")
        self.query_one("#status-badge", Static).update("⚡ Status: Execution Error")
        self.query_one("#console-scroll", ScrollPane).scroll_end(animate=False)

        exec_fail_entry = (
            f"\n\n---\n\n### ❌ Code Execution Error\n"
            f"```text\n{error}\n```"
        )
        if self.dialogue_history and self.dialogue_history[-1]["role"] == "assistant":
            if "### ❌ Code Execution Error" not in self.dialogue_history[-1]["content"]:
                self.dialogue_history[-1]["content"] += exec_fail_entry
                self._render_conversation()
                self._update_raw_display()

        self.notify(f"Execution crashed: {error}", severity="error")

    def action_copy_code(self) -> None:
        code_to_copy = self.current_code.strip()
        if not code_to_copy:
            self.notify("No code to copy!", severity="warning")
            return

        try:
            pyperclip.copy(code_to_copy)
            self.notify("Code copied to clipboard!", severity="information")
        except Exception as e:
            self.notify(f"Copy failed: {e}", severity="error")

    def action_clear_all(self) -> None:
        self.bot.reset_conversation()
        self.dialogue_history.clear()
        self.current_code = ""
        self._render_conversation()
        self._update_raw_display()
        self._update_code_display()
        self.query_one("#console-output", Static).update("Terminal cleared.")
        self.query_one("#status-badge", Static).update("⚡ Status: Cleared")
        self.notify("Context and workbench reset.", severity="information")

    def action_focus_input(self) -> None:
        self.query_one("#chat-input", Input).focus()


def run_tui(bot: Optional[JesseCodingBot] = None) -> None:
    app = JesseTUIApp(bot=bot)
    app.run()


if __name__ == "__main__":
    run_tui()
