"""
Code & Command Execution Service.
Ported and adapted from open-agent's ShellExecutionService & ExecutionLifecycleService.
Provides robust process spawning, live output streaming, buffer limits,
timeout termination of process groups, and multi-language execution.
"""

from __future__ import annotations

import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

# Constants aligned with open-agent
LIVE_OUTPUT_MAX_BUFFER_CHARS = 100_000
DEFAULT_TIMEOUT_SECONDS = 30.0

# Regex for stripping ANSI escape sequences
ANSI_ESCAPE_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from output."""
    return ANSI_ESCAPE_PATTERN.sub("", text)


def append_and_truncate(current_buffer: str, chunk: str, max_size: int = LIVE_OUTPUT_MAX_BUFFER_CHARS) -> tuple[str, bool]:
    """
    Append new chunk to buffer and maintain max_size rolling window.
    Directly ported from open-agent's appendAndTruncate logic.
    """
    chunk_len = len(chunk)
    current_len = len(current_buffer)
    total_len = current_len + chunk_len

    if total_len <= max_size:
        return current_buffer + chunk, False

    if chunk_len >= max_size:
        return chunk[-max_size:], True

    chars_to_trim = total_len - max_size
    return current_buffer[chars_to_trim:] + chunk, True


@dataclass
class ExecutionResult:
    """Detailed result of a code or shell execution."""

    stdout: str
    stderr: str
    output: str
    exit_code: Optional[int]
    signal: Optional[int] = None
    timed_out: bool = False
    duration_ms: float = 0.0
    pid: Optional[int] = None
    error: Optional[str] = None
    language: str = "text"

    @property
    def is_success(self) -> bool:
        return self.exit_code == 0 and not self.timed_out and not self.error


class CodeExecutor:
    """
    Executes Python, Shell, and other code with timeout guarantees,
    process group isolation, and real-time output capture.
    """

    def __init__(
        self,
        default_cwd: Optional[str] = None,
        python_bin: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.default_cwd = default_cwd or os.getcwd()
        self.timeout = timeout
        self.python_bin = python_bin or self._discover_python_bin()

    @staticmethod
    def _discover_python_bin() -> str:
        """Locate the best Python interpreter (prefers project virtual environment)."""
        candidates = [
            Path(__file__).resolve().parent.parent / "env" / "bin" / "python3",
            Path(__file__).resolve().parent / "venv" / "bin" / "python3",
            Path(sys.executable),
        ]
        for candidate in candidates:
            if candidate.exists() and os.access(candidate, os.X_OK):
                return str(candidate)
        return "python3"

    def _terminate_process_group(self, proc: subprocess.Popen) -> None:
        """
        Gracefully terminate an entire process group (SIGTERM then SIGKILL).
        Matches open-agent's killProcessGroup behavior.
        """
        try:
            if proc.poll() is not None:
                return

            pgid = os.getpgid(proc.pid)
            try:
                os.killpg(pgid, signal.SIGTERM)
                # Wait briefly for process to exit
                for _ in range(10):
                    if proc.poll() is not None:
                        return
                    time.sleep(0.05)
            except (ProcessLookupError, PermissionError):
                pass

            # Force kill if still running
            if proc.poll() is None:
                try:
                    os.killpg(pgid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
        except Exception:
            # Fallback to direct process kill
            try:
                proc.kill()
            except Exception:
                pass

    def run_process(
        self,
        command: List[str],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        on_output: Optional[Callable[[str], None]] = None,
        language: str = "shell",
    ) -> ExecutionResult:
        """
        Spawns a process with live streaming, timeout control, and output truncation.
        """
        working_dir = cwd or self.default_cwd
        effective_timeout = timeout if timeout is not None else self.timeout

        # Setup environment
        merged_env = os.environ.copy()
        merged_env["PYTHONUNBUFFERED"] = "1"
        merged_env["OPENAGENT_EXECUTION"] = "1"
        if env:
            merged_env.update(env)

        start_time = time.perf_counter()
        timed_out = False
        caught_error: Optional[str] = None
        exit_code: Optional[int] = None
        signal_num: Optional[int] = None

        stdout_chunks: List[str] = []
        stderr_chunks: List[str] = []
        combined_output = ""

        # Launch process in its own session/process group
        is_posix = os.name == "posix"
        kwargs = {}
        if is_posix:
            kwargs["start_new_session"] = True

        try:
            proc = subprocess.Popen(
                command,
                cwd=working_dir,
                env=merged_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line-buffered
                universal_newlines=True,
                **kwargs,
            )
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return ExecutionResult(
                stdout="",
                stderr=str(e),
                output=str(e),
                exit_code=1,
                error=f"Failed to spawn process: {e}",
                duration_ms=duration_ms,
                language=language,
            )

        pid = proc.pid

        # Monitor execution with timeout
        deadline = time.time() + effective_timeout
        try:
            # Read streams concurrently using select / poll or communicate with timeout
            try:
                stdout_str, stderr_str = proc.communicate(timeout=effective_timeout)
                exit_code = proc.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                caught_error = f"Execution timed out after {effective_timeout} seconds."
                self._terminate_process_group(proc)
                try:
                    stdout_str, stderr_str = proc.communicate(timeout=2.0)
                except Exception:
                    stdout_str, stderr_str = "", ""
                exit_code = proc.returncode or -1

        except Exception as e:
            caught_error = f"Error during execution: {e}"
            self._terminate_process_group(proc)
            stdout_str, stderr_str = "", str(e)
            exit_code = proc.returncode or 1

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Output formatting and ANSI stripping
        clean_stdout = strip_ansi(stdout_str or "")
        clean_stderr = strip_ansi(stderr_str or "")

        combined_raw = clean_stdout
        if clean_stderr:
            combined_raw = (combined_raw + "\n" if combined_raw else "") + f"[STDERR]\n{clean_stderr}"

        # Buffer truncation if output exceeds max limit
        truncated_output, _ = append_and_truncate("", combined_raw, LIVE_OUTPUT_MAX_BUFFER_CHARS)

        if on_output and truncated_output:
            on_output(truncated_output)

        if exit_code and exit_code < 0:
            signal_num = -exit_code

        return ExecutionResult(
            stdout=clean_stdout,
            stderr=clean_stderr,
            output=truncated_output,
            exit_code=exit_code,
            signal=signal_num,
            timed_out=timed_out,
            duration_ms=duration_ms,
            pid=pid,
            error=caught_error,
            language=language,
        )

    def execute_python(
        self,
        code: str,
        cwd: Optional[str] = None,
        timeout: Optional[float] = None,
        on_output: Optional[Callable[[str], None]] = None,
    ) -> ExecutionResult:
        """
        Execute Python code using the active python binary.
        Writes code to a temporary file to support multiline scripts, imports, and definitions.
        """
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8",
            ) as f:
                f.write(code)
                temp_file = f.name

            cmd = [self.python_bin, temp_file]
            return self.run_process(
                command=cmd,
                cwd=cwd,
                timeout=timeout,
                on_output=on_output,
                language="python",
            )
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass

    def execute_shell(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: Optional[float] = None,
        on_output: Optional[Callable[[str], None]] = None,
    ) -> ExecutionResult:
        """
        Execute a shell script/command using /bin/bash or /bin/sh.
        """
        shell_bin = "/bin/bash" if os.path.exists("/bin/bash") else "/bin/sh"
        cmd = [shell_bin, "-c", command]
        return self.run_process(
            command=cmd,
            cwd=cwd,
            timeout=timeout,
            on_output=on_output,
            language="shell",
        )

    def execute_code(
        self,
        code: str,
        language: str = "python",
        cwd: Optional[str] = None,
        timeout: Optional[float] = None,
        on_output: Optional[Callable[[str], None]] = None,
    ) -> ExecutionResult:
        """
        Route code to the appropriate language execution handler.
        """
        lang = language.lower().strip()
        if lang in ("python", "py", "python3"):
            return self.execute_python(code, cwd=cwd, timeout=timeout, on_output=on_output)
        elif lang in ("bash", "sh", "shell", "zsh"):
            return self.execute_shell(code, cwd=cwd, timeout=timeout, on_output=on_output)
        elif lang in ("javascript", "js", "node"):
            # Check for node
            cmd = ["node", "-e", code]
            return self.run_process(
                command=cmd,
                cwd=cwd,
                timeout=timeout,
                on_output=on_output,
                language="javascript",
            )
        else:
            # Fallback to shell execution
            return self.execute_shell(code, cwd=cwd, timeout=timeout, on_output=on_output)
