# JesseCoder ⚡

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: Passing](https://img.shields.io/badge/tests-43%20passed-brightgreen.svg)](tests/)

**JesseCoder** is a general-purpose, production-grade AI coding assistant and execution workbench built on the Jesse API (OpenAI-compatible). It features real-time Server-Sent Events (SSE) token streaming, isolated subprocess code execution with rolling buffer truncation, a terminal UI (TUI), and an automated benchmarking & multi-model evaluation test harness.

---

## 🧠 About Jesse: The Zero-Weight, Non-Neural Coding Engine

> "Jesse V1 is a zero-weight, non-neural coding model. Instead of predicting tokens like GPT or Claude, it uses program structure, graph matching, Bayesian memory, and compiler feedback. The goal is faster, cheaper, deterministic code repair and generation. The interesting question is how well it scales to real-world software."

Check Jesse built-in CAD software for [@solidSF](https://solidsf.com/).

### 🌐 Official Platforms & Interactive Playground
- **SolidSF Official CAD Platform**: [https://solidsf.com/](https://solidsf.com/) — Next-generation CAD powered by Jesse.
- **Interactive Playground**: [https://jesse.my/#playground](https://jesse.my/#playground) — Try Jesse out live with an **Unlimited API per day**!
- **API Endpoint**: `https://jesse.solidsf.com/api/v1`

---

## 🌟 Key Capabilities

- **General-Purpose Coding Agent**: Writes, debugs, and refactors code across any problem domain without synthetic mocks or hardcoded task solutions.
- **Isolated Subprocess Execution Sandbox**: Executes Python, C++, JavaScript (Node.js), and Shell scripts in detached process groups (`setsid` / `start_new_session=True`), enforcing strict timeouts (SIGTERM ➔ SIGKILL) and live streaming standard input/output.
- **Real-Time Token Streaming**: Streams code and explanations token-by-token directly from Jesse API models using SSE over FastAPI or WebSockets.
- **Multiple User Interfaces**:
  - **Modern Web Console**: Interactive browser-based coding workbench with model picker, raw payload inspection, and live console execution.
  - **Textual TUI**: Terminal-based user interface with side-by-side stream viewers and keyboard navigation.
  - **CLI Runner**: Interactive multi-turn terminal chat or single-shot command-line generation.
- **Automated Testing & Multi-Model Evaluation**: Automated test suite executing benchmark problem sets with standard input (`stdin`) against `jesse-prod`, `jesse-pristine`, and `jesse`.
- **Clean Root Architecture**: Zero coding files in root directory; strictly structured into `source/`, `scripts/`, `testing/`, `tests/`, and `web/`.
- **Zero Secrets In Source**: Strictly environment-variable driven via `.env.example` with runtime key masking and no committed credentials.

---

## 📂 Project Architecture & Structure

The repository follows a clean, professional architecture where the root folder strictly contains only markdown, documentation, and configuration files (**zero coding or script files in root**):

```
jesse-coder/
├── source/                       # All Python application & package source code
│   ├── jesse_coder/              # Modular library package
│   │   ├── __init__.py           # Package exports & versioning
│   │   ├── bot.py                # Orchestrator & multi-turn agent logic
│   │   ├── cli.py                # Interactive CLI entrypoint
│   │   ├── client.py             # Jesse OpenAI-compatible API client
│   │   ├── code_extractor.py     # Robust fenced code & tool action extractor
│   │   ├── config.py             # Dynamic configuration & environment loader
│   │   ├── conversation.py       # Sliding-window context & message history
│   │   ├── exceptions.py         # Domain-specific exception hierarchy
│   │   ├── executor.py           # Process-isolated sandboxed code execution
│   │   ├── tui.py                # Textual terminal user interface
│   │   └── web_server.py         # FastAPI backend with SSE streaming
│   ├── bot.py                    # Module aliases & standalone exports
│   ├── cli.py
│   ├── client.py
│   ├── code_extractor.py
│   ├── config.py
│   ├── conversation.py
│   ├── exceptions.py
│   ├── executor.py
│   ├── main.py                   # CLI entrypoint runner
│   ├── run_tests.py
│   ├── synthesizer.py
│   ├── tui.py
│   ├── tui_app.py                # Textual TUI launcher
│   ├── web_app.py                # WebApp server launcher
│   └── web_server.py
├── scripts/                      # Shell automation scripts (NO scripts in root)
│   ├── run.sh                    # Interactive CLI & TUI launcher
│   ├── run_web.sh                # WebApp server launcher
│   └── build_frontend.sh         # Frontend asset bundler
├── testing/                      # Automated benchmark & evaluation suite
│   ├── automated_testing.py      # Multi-model test runner with stdin streaming
│   ├── tasks.json                # Standard 10 algorithmic benchmark tasks
│   ├── tasks_complex.json        # Advanced algorithmic task set 2
│   ├── tasks_all.json            # Full 20-task benchmark suite
│   ├── TASK_EVAL_REPORT.md       # Detailed task-by-task execution report
│   ├── MODEL_COMPARISON_REPORT.md# Cross-model evaluation matrix
│   └── README.md                 # Testing suite documentation
├── tests/                        # Comprehensive unit & integration tests
│   ├── test_client.py            # API error mapping & retry tests
│   ├── test_config.py            # Configuration validation tests
│   ├── test_conversation.py      # Sliding-window conversation tests
│   ├── test_executor.py          # Process isolation, ANSI stripping, and timeouts
│   ├── test_live.py              # End-to-end live API integration tests
│   ├── test_tui.py               # Terminal UI widget tests
│   └── test_web_server.py        # FastAPI endpoint integration tests
├── web/                          # Frontend WebApp assets
│   ├── static/                   # Production HTML, CSS, and JS bundle
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── bundle.js
│   ├── src/                      # TypeScript source files
│   │   └── app.ts
│   ├── package.json              # WebApp build configuration
│   └── build.js                  # Frontend bundle script
├── .env.example                  # Template configuration without secrets
├── .gitignore                    # Comprehensive Git ignore rules (cache, env, keys)
├── LICENSE                       # MIT License
├── pyproject.toml                # Modern Python packaging configuration
├── pytest.ini                    # Pytest configuration (pythonpath configured for source/)
├── README.md                     # Documentation
└── requirements.txt              # Production dependency specifications
```

---

## 🚀 Quickstart & Installation

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/haseeb-heaven/jesse-coder.git
cd jesse-coder

python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the template `.env.example` file to `.env` and insert your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# Jesse API Credentials
JESSE_API_KEY=your_api_key_here
JESSE_BASE_URL=https://jesse.solidsf.com/api/v1
JESSE_MODEL=jesse-prod
JESSE_TEMPERATURE=0.2
JESSE_TIMEOUT=60.0
```

> **Security Note**: Never commit `.env` or files containing secret keys to Git. The `.gitignore` automatically prevents `.env` and database files from being tracked.

---

## 🖥️ Usage Interfaces

### 1. Web Console (Recommended)

Launch the interactive web application:

```bash
./scripts/run_web.sh
# OR
python3 source/web_app.py --port 8080
```

Navigate to `http://localhost:8080` in your browser. Features include:
- Real-time token streaming via Server-Sent Events.
- Live isolated code execution (`Ctrl+E` or clicking **Run Code**).
- Dynamic model picker switching between `jesse-prod`, `jesse-pristine`, and `jesse`.
- Raw API payload inspector (`Ctrl+R`).

### 2. Interactive CLI

Launch the interactive terminal session:

```bash
./scripts/run.sh
# OR
python3 source/main.py
```

Execute a single-shot prompt directly with auto-execution:

```bash
python3 source/main.py --prompt "Write a Python script to compute the 10th Fibonacci number" --exec
```

Available interactive commands in CLI:
- `/exec`: Execute the last extracted code block.
- `/code`: View the raw extracted code.
- `/model <name>`: Switch the active model (`jesse-prod`, `jesse-pristine`, `jesse`).
- `/reset`: Clear conversation context memory.
- `/autoexec`: Toggle automatic code execution.
- `/exit`: Terminate session.

### 3. Terminal UI (TUI)

Launch the full-screen terminal interface built with Textual:

```bash
./scripts/run.sh tui
# OR
python3 source/tui_app.py
```

---

## 🧪 Automated Testing & Benchmarking

The [`testing/`](testing/) directory contains an automated testing harness for feeding algorithmic tasks to Jesse models, compiling/executing them against standard input (`stdin`), and verifying outputs against expected results.

### Running Automated Tests

```bash
# Run all benchmark tasks against default model (jesse-prod)
python3 testing/automated_testing.py

# Run only Python tasks
python3 testing/automated_testing.py --lang python

# Run multi-model comparison across all 3 models (jesse-prod, jesse-pristine, jesse)
python3 testing/automated_testing.py --all-models

# Run a specific task ID
python3 testing/automated_testing.py --task task_02

# Run complex benchmark task set 2
python3 testing/automated_testing.py --tasks-file testing/tasks_complex.json
```

---

## 🔬 Unit & Integration Tests

Run the full pytest suite:

```bash
pytest tests -v
```

All 43 unit and integration tests verify:
- API authentication, rate limiting, and network timeout error translations.
- Memory history sliding windows and serialization.
- Subprocess isolation, ANSI terminal escape stripping, and process termination.
- FastAPI endpoints (`/api/health`, `/api/model`, `/api/chat/stream`, `/api/execute`).
- Live streaming and multi-turn conversation parity.

---

## 🔒 Security & Safe Execution

- **Process Isolation**: Every script executes in its own session (`os.setsid`) to prevent rogue child processes from lingering.
- **Graceful Termination**: Processes exceeding the configured timeout receive `SIGTERM`, followed by `SIGKILL` if unresponsive.
- **Buffer Safety**: Live execution streams cap memory consumption at 100,000 characters to prevent memory exhaustion.
- **Secret Protection**: API keys are masked in logs and exceptions (`jess...0001`), and never hardcoded in source files.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
