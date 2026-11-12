"""Execute the official A01-A20 Part C acceptance cases.

The workflow also commits the generated transcript and JSONL evidence after a passing run.

Run from the repository root:
    python scripts/run_part_c_acceptance.py

This is separate from scripts/run_acceptance.py, which validates Part A.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Keep weather results deterministic and offline during acceptance execution.
os.environ["WEATHER_MODE"] = "stub"
os.environ["AGENT_LOG_PATH"] = str(ROOT / "logs" / "runs.jsonl")

from agent.run_agent import Agent  # noqa: E402

GOLDEN_SET = ROOT / "eval" / "golden_set.csv"
LOG_PATH = ROOT / "logs" / "runs.jsonl"
TRANSCRIPT_PATH = ROOT / "outputs" / "acceptance_transcript.md"

REQUIRED_LOG_FIELDS = {
    "run_id", "user_id", "session_id", "timestamp", "question", "intent",
    "confidence", "route", "executed", "attempts", "tools_called", "status",
    "answer_text", "evidence", "grounded_values", "latency_ms", "tokens_est",
    "tool_calls", "ungrounded_numbers", "ungrounded_claims", "budget_exceeded",
}


def load_cases():
    with GOLDEN_SET.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    cases = [row for row in rows if row["case_id"].startswith("A")]
    cases.sort(key=lambda row: row["case_id"])
    if [row["case_id"] for row in cases] != [f"A{i:02d}" for i in range(1, 21)]:
        raise ValueError("Golden set must contain exactly A01-A20 for Part C acceptance.")
    return cases


def main() -> int:
    cases = load_cases()
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    TRANSCRIPT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Start a clean, dedicated acceptance log; no other log file is touched.
    LOG_PATH.write_text("", encoding="utf-8")
    agent = Agent(data_dir=str(ROOT / "data"), log_path=str(LOG_PATH))
    results = []
    try:
        for case in cases:
            result = agent.handle(
                case["question"],
                session_id=case["session_id"],
                simulate_failures=int(case["simulate_failures"]),
            )
            expected_fragments = [
                part.strip().casefold()
                for part in case["expected_contains"].split("|")
                if part.strip()
            ]
            response = result["answer_text"].casefold()
            content_ok = all(fragment in response for fragment in expected_fragments)
            checks = {
                "status": result["final_status"] == case["expected_status"],
                "intent": result["intent"] == case["expected_intent"],
                "response_content": content_ok,
                "grounding": result["ungrounded_numbers"] == 0,
                "retry_limit": result["attempts"] <= 3,
            }
            results.append({
                "case_id": case["case_id"],
                "question": case["question"],
                "expected_status": case["expected_status"],
                "actual_status": result["final_status"],
                "expected_intent": case["expected_intent"],
                "actual_intent": result["intent"],
                "expected_contains": case["expected_contains"],
                "actual_response": result["answer_text"],
                "attempts": result["attempts"],
                "ungrounded_numbers": result["ungrounded_numbers"],
                "checks": checks,
                "passed": all(checks.values()),
            })
    finally:
        agent.con.close()

    raw_lines = [
        line for line in LOG_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    records = [json.loads(line) for line in raw_lines]
    log_schema_ok = (
        len(records) == 20
        and all(REQUIRED_LOG_FIELDS.issubset(record) for record in records)
    )
    log_grounding_ok = all(record.get("ungrounded_numbers") == 0 for record in records)
    passed = sum(row["passed"] for row in results)
    overall = "PASS" if passed == 20 and log_schema_ok and log_grounding_ok else "FAIL"

    lines = [
        "# Part C — Agent Acceptance Test Transcript",
        "",
        f"**Overall status:** {overall} — {passed}/20 cases passed.",
        "",
        f"**Executed (UTC):** {datetime.now(timezone.utc).isoformat()}",
        "",
        "**Command:** `python scripts/run_part_c_acceptance.py`",
        "",
        "**Input:** Official Part C acceptance rows A01–A20 from `eval/golden_set.csv`.",
        "",
        "**Weather mode:** Deterministic offline stub (`WEATHER_MODE=stub`).",
        "",
        f"**Audit log:** `logs/runs.jsonl` — {len(records)} JSONL records.",
        "",
        "## Acceptance results",
        "",
        "| Case | Expected status | Actual status | Expected intent | Actual intent | Result |",
        "|---|---|---|---|---|---|",
    ]
    for row in results:
        lines.append(
            f"| {row['case_id']} | {row['expected_status']} | {row['actual_status']} "
            f"| {row['expected_intent']} | {row['actual_intent']} "
            f"| {'PASS' if row['passed'] else 'FAIL'} |"
        )
        lines.extend([
            "",
            f"### {row['case_id']} — {row['question']}",
            "",
            f"**Actual response:** {row['actual_response']}",
            "",
            f"**Expected response content:** `{row['expected_contains']}`",
            "",
            "**Checks:** " + "; ".join(
                f"{name}={'PASS' if ok else 'FAIL'}"
                for name, ok in row["checks"].items()
            ),
            "",
            f"**Query attempts:** {row['attempts']}  ",
            f"**Ungrounded numeric claims:** {row['ungrounded_numbers']}",
            "",
        ])

    lines.extend([
        "## Audit-log validation",
        "",
        f"- Expected JSONL records: 20",
        f"- Actual JSONL records: {len(records)}",
        f"- Required schema: {'PASS' if log_schema_ok else 'FAIL'}",
        f"- Zero ungrounded numeric claims: {'PASS' if log_grounding_ok else 'FAIL'}",
        f"- Overall Part C acceptance: **{overall}**",
        "",
    ])
    TRANSCRIPT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Part C acceptance: {passed}/20 cases passed.")
    print(f"JSONL records: {len(records)}; schema: {'PASS' if log_schema_ok else 'FAIL'}.")
    print(f"Grounding audit: {'PASS' if log_grounding_ok else 'FAIL'}.")
    print(f"Transcript: {TRANSCRIPT_PATH.relative_to(ROOT)}")
    print(f"Overall: {overall}")
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
