# Jesse Coding Chatbot (Autonomous Engineering Agent)

A modular, production-ready Python coding chatbot built to interface with the Jesse API (`jesse.solidsf.com` / `api.jesse.my`). It features real-time token streaming, complete try/catch error handling with domain exceptions, conversational context memory, and an interactive terminal CLI.

---

## 📁 Architecture & Modularity

```
Python/jesse-coder/
├── .env                  # Pre-configured credentials & endpoint
├── requirements.txt      # Python dependencies (openai, pytest, python-dotenv)
├── __init__.py           # Public exports (JesseConfig, JesseClient, JesseCodingBot, CodeExecutor, etc.)
├── config.py             # Configuration dataclass with validation and defaults
├── exceptions.py         # Custom exception hierarchy (Auth, Connection, RateLimit, Server, Stream)
├── conversation.py       # Multi-turn history manager with context windowing & rollback
├── client.py             # Low-level client with full try/except mapping and token streaming
├── web/                  # Modern TypeScript WebApp frontend
│   ├── src/              # TypeScript source files
│   │   ├── types.ts      # Data types (ChatMessage, ExecutionResult, etc.)
│   │   ├── api.ts        # SSE stream consumer & execution client
│   │   ├── markdown.ts   # Safe markdown renderer with syntax blocks
│   │   ├── ui.ts         # UI DOM & workbench controller
│   │   └── app.ts        # Main TypeScript application coordinator
│   ├── static/           # Static distribution files
│   │   ├── index.html    # Two-column responsive HTML matching jev-system-one theme
│   │   ├── style.css     # Cyber-slate custom styles
│   │   └── bundle.js     # Bundled TypeScript application
│   └── tsconfig.json     # TypeScript configuration
├── web_server.py         # FastAPI backend with SSE streaming & code execution
├── web_app.py            # 1-click Python launcher for WebApp on port 8080
├── build_frontend.sh     # Compiles TypeScript source to web/static/bundle.js
├── run_web.sh            # 1-click bash launcher for WebApp
├── executor.py           # Code & shell execution engine ported from open-agent ShellExecutionService
├── code_extractor.py     # Parser for markdown blocks (```python, ```bash), tool actions & raw code
├── bot.py                # High-level orchestrator managing turns, streaming, extraction & execution
├── cli.py                # Interactive colored REPL with /exec, /code, /autoexec, /history, /clear
├── tui.py                # Textual TUI with streaming chat, code workbench & execution terminal
├── tui_app.py            # 1-click launcher for Textual TUI interface
├── main.py               # CLI entrypoint supporting interactive mode, one-shot prompt, --exec, and --web
├── chat.py               # Direct 1-click launcher for interactive chatbot
├── example_stream.py     # Standalone streaming quickstart script
├── run_tests.py          # Standalone 1-click test runner
├── run.sh                # Bash script with automatic venv detection
├── pytest.ini            # Pytest configuration
└── tests/
    ├── test_config.py        # Settings validation & boundary tests
    ├── test_conversation.py  # Chat history, windowing & serialization tests
    ├── test_client.py        # Exception translation & stream parser unit tests
    ├── test_executor.py      # Code execution, process group termination & extraction tests
    ├── test_live.py          # Live integration tests against Jesse API
    ├── test_tui.py           # Textual TUI composition and interactive action tests
    └── test_web_server.py    # FastAPI endpoints, SSE streaming, and execution tests
```

---

## ⚙️ Configuration & Credentials

The bot is pre-configured with the default test credentials provided:
- **API Key**: `jesse_test_demo00000000000000000000000001`
- **Base URL**: `https://jesse.solidsf.com/api/v1`
- **Default Model**: `jesse-prod` (also supports `jesse-pristine`)

You can override these via environment variables or direct arguments:
- `JESSE_API_KEY`
- `JESSE_BASE_URL`
- `JESSE_MODEL`
- `JESSE_TEMPERATURE`

---

## 🚀 How to Run

### 1. Modern Textual TUI Interface (Recommended)
Launch the multi-pane cyberpunk TUI workbench with real-time streaming, interactive code executor, copy-to-clipboard button, and language selector:
```bash
./run.sh tui
# or
/Users/haseeb-mir/Documents/Code/Python/env/bin/python3 tui_app.py
```

**TUI Keybindings & Controls:**
- `ctrl+q` — Quit
- `ctrl+e` — Execute current code
- `ctrl+y` — Copy code to clipboard
- `ctrl+l` — Clear conversation and workbench
- `ctrl+r` — Focus prompt input
- `▶ Run Code` button — One-click code execution via open-agent engine
- `📋 Copy Code` button — Copy code with toast notification
- `Choose Language` dropdown — Select between Python, Bash, Node.js, Rust, C++

### 2. Interactive Terminal CLI
Run standard terminal REPL:
```bash
./run.sh
# or
/Users/haseeb-mir/Documents/Code/Python/env/bin/python3 -m jesse-coder.main
```

Inside the chatbot, you can chat directly or use slash commands:
- `/help` - Show command list
- `/clear` - Clear conversation history and reset context
- `/history` - Display the current conversation turns
- `/model <name>` - Switch between `jesse-prod` and `jesse-pristine`
- `/exit` or `/quit` - Exit the chatbot

### 2. One-Shot Streaming Prompt
```bash
/Users/haseeb-mir/Documents/Code/Python/env/bin/python3 -m jesse-coder.main --prompt "Write a Python function to merge two sorted lists"
```

### 3. Quickstart Example Script
```bash
/Users/haseeb-mir/Documents/Code/Python/env/bin/python3 jesse-coder/example_stream.py
```

---

## 💻 Python Library Usage

```python
from jesse-coder import JesseCodingBot, JesseConfig, JesseBotError
import sys

config = JesseConfig(
    api_key="jesse_test_demo00000000000000000000000001",
    base_url="https://jesse.solidsf.com/api/v1",
    model="jesse-prod",
    temperature=0.2,
)

bot = JesseCodingBot(config=config)

try:
    print("Jesse: ", end="", flush=True)
    for token in bot.ask_stream("Explain the difference between a process and a thread"):
        sys.stdout.write(token)
        sys.stdout.flush()
    print()

except JesseBotError as e:
    print(f"Error communicating with Jesse: {e}")
```

---

## ⚡ Code Execution Engine (Ported from open-agent)

The code execution engine is directly ported from **open-agent** (`ShellExecutionService` & `ExecutionLifecycleService`) and converted to native Python:

- **Intelligent Code Extraction** (`code_extractor.py`):
  - Automatically parses markdown code blocks (````python ... ````, ````bash ... ````, ````sh ... ````, ````node ... ````).
  - Detects tool action calls (`<actions> [ { "name": "Bash", "args": { "command": "..." } } ]`).
  - Fallbacks to clean raw code detection.

- **Robust Process Management** (`executor.py`):
  - **Process Group Isolation**: Sets independent sessions (`start_new_session=True` / `setsid`).
  - **Timeout Protection**: Automatically kills unresponsive scripts (SIGTERM -> graceful wait -> SIGKILL).
  - **Buffer & Rolling Truncation**: Enforces open-agent's `LIVE_OUTPUT_MAX_BUFFER_CHARS` (100,000 chars) to protect memory.
  - **ANSI Stripping**: Cleans terminal color codes from output buffers.
  - **Environment Sanitization**: Sets `PYTHONUNBUFFERED=1`, links the active virtual environment python interpreter.

### Interactive Execution Commands:
- `/exec` - Executes the latest code block generated by Jesse and prints a formatted execution box.
- `/code` - Displays the raw extracted code block from the current turn.
- `/autoexec` - Toggles auto-execution on or off for all upcoming turns.

### CLI Auto-Execution:
```bash
./run.sh --prompt "Write a Python script to print the first 10 Fibonacci numbers" --exec
```

Every API and runtime error is captured and translated into structured domain exceptions:

| Exception | Root Cause |
|---|---|
| `JesseAuthenticationError` | 401 Unauthorized / 403 Forbidden (Invalid or expired API key) |
| `JesseConnectionError` | DNS failures, connection timeouts, unreachable endpoint |
| `JesseRateLimitError` | 429 Rate limit or quota exceeded |
| `JesseBadRequestError` | 400 Bad request / invalid parameter |
| `JesseServerError` | 500+ Remote upstream server failure |
| `JesseStreamError` | Network interruption or malformed token chunks mid-stream |
| `JesseConfigError` | Invalid URL, empty key, or temperature out of range [0.0, 2.0] |

---

## 🧪 Running Tests

Run all unit and live integration tests:
```bash
/Users/haseeb-mir/Documents/Code/Python/env/bin/python3 -m pytest jesse-coder/tests -c jesse-coder/pytest.ini -v
```
All 21 tests pass across configuration, conversation memory, client error mappings, and live API endpoints.
