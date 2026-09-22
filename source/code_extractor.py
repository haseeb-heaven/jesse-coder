"""
Code extraction module.
Parses LLM responses to detect and extract code blocks (Python, Shell/Bash, JS, etc.)
or identify pure code content safely without executing plain prose.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ExtractedCodeBlock:
    """Represents a code block extracted from an LLM response."""

    language: str
    code: str
    start_index: int
    end_index: int

    @property
    def is_python(self) -> bool:
        return self.language.lower() in ("python", "py", "python3")

    @property
    def is_shell(self) -> bool:
        return self.language.lower() in ("bash", "sh", "shell", "zsh")

    @property
    def is_javascript(self) -> bool:
        return self.language.lower() in ("javascript", "js", "node", "typescript", "ts")

    @property
    def is_cpp(self) -> bool:
        return self.language.lower() in ("cpp", "c++", "cc", "cxx", "c")


# Regex to match markdown fenced code blocks: ```lang ... ```
CODE_BLOCK_REGEX = re.compile(
    r"```(?P<lang>[a-zA-Z0-9_\-\+\.#]*)\s*\n(?P<code>.*?)```",
    re.DOTALL,
)

# Regex to match unclosed trailing markdown code blocks: ```lang ... <EOF>
UNCLOSED_CODE_BLOCK_REGEX = re.compile(
    r"```(?P<lang>[a-zA-Z0-9_\-\+\.#]*)\s*\n(?P<code>.+)$",
    re.DOTALL,
)


def extract_code_blocks(text: str) -> List[ExtractedCodeBlock]:
    """
    Extract all fenced markdown code blocks from a string.

    Args:
        text: The model response or markdown string.

    Returns:
        List of ExtractedCodeBlock objects found in the text.
    """
    blocks: List[ExtractedCodeBlock] = []
    if not text:
        return blocks

    # 1. Closed code blocks
    for match in CODE_BLOCK_REGEX.finditer(text):
        lang = match.group("lang").strip().lower() or "python"
        code = match.group("code")
        blocks.append(
            ExtractedCodeBlock(
                language=lang,
                code=code,
                start_index=match.start(),
                end_index=match.end(),
            )
        )

    # 2. If no closed blocks, check for an unclosed trailing code block (e.g. streaming or truncated)
    if not blocks:
        match = UNCLOSED_CODE_BLOCK_REGEX.search(text)
        if match:
            lang = match.group("lang").strip().lower() or "python"
            code = match.group("code")
            blocks.append(
                ExtractedCodeBlock(
                    language=lang,
                    code=code,
                    start_index=match.start(),
                    end_index=match.end(),
                )
            )

    return blocks


def get_primary_code_block(
    text: str, preferred_lang: Optional[str] = None
) -> Optional[ExtractedCodeBlock]:
    """
    Extract the primary or most relevant code block from text.
    Prioritizes fenced code blocks, then action JSON commands, then verified raw code.
    Never treats arbitrary conversational text as code.

    Args:
        text: The text to search.
        preferred_lang: Preferred language hint ('python', 'bash', etc.).

    Returns:
        The best matching ExtractedCodeBlock, or None if no valid code is found.
    """
    if not text or not text.strip():
        return None

    blocks = extract_code_blocks(text)

    # 1. Return preferred language if requested from fenced blocks
    if preferred_lang and blocks:
        pref = preferred_lang.lower()
        for b in blocks:
            if (
                b.language == pref
                or (pref in ("bash", "sh") and b.is_shell)
                or (pref in ("python", "py", "python3") and b.is_python)
                or (pref in ("javascript", "js", "node") and b.is_javascript)
                or (pref in ("cpp", "c++", "cxx", "cc") and b.is_cpp)
            ):
                return b

    # 2. Prefer the largest Python block, then largest shell block, then largest of anything
    if blocks:
        python_blocks = [b for b in blocks if b.is_python]
        if python_blocks:
            return max(python_blocks, key=lambda b: len(b.code.strip()))
        shell_blocks = [b for b in blocks if b.is_shell]
        if shell_blocks:
            return max(shell_blocks, key=lambda b: len(b.code.strip()))
        return max(blocks, key=lambda b: len(b.code.strip()))

    # 3. Check for tool action calls like {"name": "Bash", "args": {"command": "..."}}
    action_match = re.search(
        r'"name":\s*"(?:Bash|bash|sh|shell)"\s*,\s*"args":\s*\{\s*"command":\s*"(?P<cmd>(?:\\.|[^"\\])*)"',
        text,
        re.IGNORECASE,
    )
    if action_match:
        raw_cmd = action_match.group("cmd").encode("utf-8").decode("unicode_escape")
        return ExtractedCodeBlock(language="bash", code=raw_cmd, start_index=action_match.start(), end_index=action_match.end())

    python_action_match = re.search(
        r'"name":\s*"(?:python|Python|python3)"\s*,\s*"args":\s*\{\s*"(?:code|command)":\s*"(?P<code>(?:\\.|[^"\\])*)"',
        text,
        re.IGNORECASE,
    )
    if python_action_match:
        raw_code = python_action_match.group("code").encode("utf-8").decode("unicode_escape")
        return ExtractedCodeBlock(language="python", code=raw_code, start_index=python_action_match.start(), end_index=python_action_match.end())

    # 4. Fallback for raw code (ONLY if it compiles as valid Python or starts with a valid shell command)
    trimmed = text.strip()
    if trimmed.startswith(("<", "Prompt:", "Reasoning:", "{", "[", "Here are", "1.", "I have", "Let me")):
        return None

    # Check if raw text is syntactically valid Python
    try:
        parsed = ast.parse(trimmed)
        # Must have at least one executable statement and not be a trivial single string
        if parsed.body:
            first_node = parsed.body[0]
            # If it's just a single string literal (like a plain text message), it's not code
            is_single_str = (
                len(parsed.body) == 1
                and isinstance(first_node, ast.Expr)
                and isinstance(getattr(first_node, "value", None), ast.Constant)
                and isinstance(first_node.value.value, str)
            )
            if not is_single_str:
                # Check that it has code-like structure (imports, definitions, assignments, calls, etc.)
                has_code_construct = any(
                    isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef,
                                      ast.ClassDef, ast.Assign, ast.AnnAssign, ast.AugAssign,
                                      ast.For, ast.While, ast.If, ast.With, ast.Try))
                    or (isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Call))
                    for node in parsed.body
                )
                if has_code_construct:
                    return ExtractedCodeBlock(language="python", code=trimmed, start_index=0, end_index=len(text))
    except (SyntaxError, ValueError, TypeError):
        pass

    # Check for shell script shebang or command
    shell_starts = ("#!/bin/bash", "#!/bin/sh", "#!/usr/bin/env bash", "#!/usr/bin/env sh")
    if any(trimmed.startswith(s) for s in shell_starts):
        return ExtractedCodeBlock(language="bash", code=trimmed, start_index=0, end_index=len(text))

    return None
