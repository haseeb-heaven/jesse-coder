"""
Task Evaluation Runner for JesseCoder.
Feeds input tasks to the Jesse model one-by-one, executes the generated code
against the provided inputs, verifies outputs, and generates a structured report.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from bot import JesseCodingBot
from code_extractor import get_primary_code_block
from executor import CodeExecutor


def normalize_output(text: str) -> str:
    """Normalize output by stripping trailing whitespace per line and overall."""
    lines = [line.rstrip() for line in (text or "").strip().splitlines()]
    return "\n".join(lines)


def build_task_prompt(task: Dict[str, Any]) -> str:
    lang = task["language"]
    title = task["title"]
    description = task["task"]
    sample_input = task["input"]
    expected_output = task["expected_output"]

    lang_instructions = {
        "python": "Read from sys.stdin and print to sys.stdout.",
        "javascript": "Read from standard input using require('fs').readFileSync(0, 'utf-8') and print using console.log.",
        "cpp": "Read from std::cin and write to std::cout.",
    }.get(lang.lower(), "Read from standard input and write to standard output.")

    return f"""\
Implement a complete, standalone program in {lang} that solves the following task:

Title: {title}
Description: {description}

Input/Output Requirements:
{lang_instructions}

Sample Input:
{sample_input}

Expected Output:
{expected_output}

STRICT REQUIREMENT:
Output ONLY the complete runnable program wrapped in ```{lang} ... ``` code block.
Do NOT output any markdown headers, conversational text, or explanations outside the code block.
"""


def run_evaluation() -> None:
    tasks_file = Path(__file__).resolve().parent / "tasks.json"
    if not tasks_file.exists():
        raise FileNotFoundError(f"tasks.json not found at {tasks_file}")

    with open(tasks_file, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    bot = JesseCodingBot()
    executor = CodeExecutor()

    results: List[Dict[str, Any]] = []
    print(f"Starting evaluation of {len(tasks)} tasks against Jesse model ({bot.config.model})...\n")

    for i, task in enumerate(tasks, start=1):
        task_id = task["id"]
        title = task["title"]
        lang = task["language"]
        expected_output = task["expected_output"]
        stdin_input = task["input"]

        print(f"[{i}/{len(tasks)}] Evaluating {task_id}: {title} ({lang})...")
        bot.reset_conversation()

        prompt = build_task_prompt(task)
        t_start = time.perf_counter()

        model_response = ""
        extracted_code = ""
        actual_output = ""
        exec_error = None
        passed = False
        duration_ms = 0.0

        try:
            # Query Jesse model
            model_response = bot.ask(prompt)
            query_time_ms = (time.perf_counter() - t_start) * 1000

            # Extract code
            code_block = get_primary_code_block(model_response, preferred_lang=lang)
            if code_block and code_block.code.strip():
                extracted_code = code_block.code.strip()
                # Execute code with task stdin
                exec_res = executor.execute_code(
                    code=extracted_code,
                    language=lang,
                    stdin_data=stdin_input,
                    timeout=20.0,
                )
                duration_ms = exec_res.duration_ms
                actual_output = exec_res.stdout

                norm_actual = normalize_output(actual_output)
                norm_expected = normalize_output(expected_output)

                passed = exec_res.is_success and (norm_actual == norm_expected)
                if not exec_res.is_success:
                    exec_error = exec_res.error or exec_res.stderr or f"Exit code {exec_res.exit_code}"
                elif not passed:
                    exec_error = f"Output mismatch.\nExpected:\n{norm_expected}\nGot:\n{norm_actual}"
            else:
                exec_error = "No valid code block extracted from model response."

        except Exception as exc:
            exec_error = f"Evaluation exception: {exc}"

        status_str = "PASS" if passed else "FAIL"
        print(f"       Status: {status_str} | Duration: {duration_ms:.1f}ms")
        if exec_error:
            first_err_line = exec_error.splitlines()[0] if exec_error else ""
            print(f"       Detail: {first_err_line}")

        results.append({
            "id": task_id,
            "title": title,
            "language": lang,
            "passed": passed,
            "duration_ms": duration_ms,
            "expected_output": expected_output,
            "actual_output": actual_output,
            "error": exec_error,
            "model_response": model_response,
            "extracted_code": extracted_code,
        })

    # Summary calculations
    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    pass_rate = (passed_count / total * 100) if total else 0.0

    print(f"\n==========================================")
    print(f"EVALUATION COMPLETE: {passed_count}/{total} Passed ({pass_rate:.1f}%)")
    print(f"==========================================\n")

    # Save JSON report
    report_json_path = Path(__file__).resolve().parent / "task_eval_report.json"
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total": total,
                "passed": passed_count,
                "failed": total - passed_count,
                "pass_rate_pct": pass_rate,
                "model": bot.config.model,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "tasks": results,
        }, f, indent=2)

    # Save Markdown report
    report_md_path = Path(__file__).resolve().parent / "TASK_EVAL_REPORT.md"
    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write(f"# JesseCoder Task Evaluation Report\n\n")
        f.write(f"- **Model**: `{bot.config.model}`\n")
        f.write(f"- **Total Tasks**: {total}\n")
        f.write(f"- **Passed**: {passed_count}\n")
        f.write(f"- **Failed**: {total - passed_count}\n")
        f.write(f"- **Pass Rate**: {pass_rate:.1f}%\n")
        f.write(f"- **Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Summary Table\n\n")
        f.write("| Task ID | Title | Language | Status | Execution Time | Notes |\n")
        f.write("| :--- | :--- | :--- | :---: | :---: | :--- |\n")
        for r in results:
            badge = "✅ PASS" if r["passed"] else "❌ FAIL"
            notes = "Matches expected output" if r["passed"] else (r["error"] or "").splitlines()[0]
            f.write(f"| `{r['id']}` | {r['title']} | `{r['language']}` | {badge} | {r['duration_ms']:.1f}ms | {notes} |\n")

        f.write("\n## Detailed Task Results\n\n")
        for r in results:
            badge = "PASS" if r["passed"] else "FAIL"
            f.write(f"### {r['id']} - {r['title']} ({r['language'].upper()}) [{badge}]\n\n")
            if r["extracted_code"]:
                f.write(f"#### Extracted Code:\n```{r['language']}\n{r['extracted_code']}\n```\n\n")
            else:
                f.write(f"#### Model Response (No Code Extracted):\n```\n{r['model_response'][:500]}\n```\n\n")

            f.write(f"#### Expected Output:\n```\n{r['expected_output']}\n```\n\n")
            f.write(f"#### Actual Output:\n```\n{r['actual_output'] or '(none)'}\n```\n\n")
            if r["error"]:
                f.write(f"#### Diagnostics:\n```\n{r['error']}\n```\n\n")
            f.write("---\n\n")

    print(f"Reports saved to:")
    print(f" - JSON: {report_json_path}")
    print(f" - Markdown: {report_md_path}")


if __name__ == "__main__":
    run_evaluation()
