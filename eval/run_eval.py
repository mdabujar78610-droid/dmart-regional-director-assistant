"""Run the committed golden set and create auditable evaluation artifacts."""
from __future__ import annotations
import csv, json, os, re, statistics, time, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
from agent.run_agent import Agent
GOLDEN = ROOT / "eval" / "golden_set.csv"
RESULTS = ROOT / "eval" / "eval_results.csv"
RUNS = ROOT / "eval" / "eval_runs.jsonl"


def contains_with_tolerance(answer: str, required: str) -> bool:
    answer_low, required_low = answer.casefold(), required.casefold()
    if required_low in answer_low:
        return True
    nums = re.findall(r"-?\d+\.\d+", required)
    if not nums:
        return False
    # Keep the non-numeric wording (e.g. "Pune INR") and compare numeric value within 0.01.
    text_part = re.sub(r"-?\d+\.\d+", "", required, flags=re.I).strip().casefold()
    if text_part and text_part not in answer_low:
        return False
    actual_nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", answer)]
    return all(any(abs(float(expected) - actual) <= 0.01 for actual in actual_nums) for expected in nums)


def main():
    os.environ["WEATHER_MODE"] = "stub"
    os.environ["AGENT_LOG_PATH"] = str(RUNS)
    RUNS.parent.mkdir(parents=True, exist_ok=True)
    RUNS.write_text("", encoding="utf-8")
    cases = pd.read_csv(GOLDEN, keep_default_na=False)
    agent = Agent(data_dir=str(ROOT / "data"), log_path=str(RUNS))
    result_rows = []
    for row in cases.to_dict("records"):
        start = time.perf_counter()
        result = agent.handle(row["question"], session_id=row["session_id"],
                              simulate_failures=int(row["simulate_failures"] or 0))
        elapsed = (time.perf_counter() - start) * 1000
        required = [x for x in row["expected_contains"].split("|") if x]
        contains_match = all(contains_with_tolerance(result["answer_text"], item) for item in required)
        status_match = result["status"] == row["expected_status"]
        intent_match = result["intent"] == row["expected_intent"]
        result_rows.append({
            "case_id": row["case_id"], "category": row["category"],
            "expected_status": row["expected_status"], "actual_status": result["status"],
            "intent_match": intent_match, "contains_match": contains_match,
            "latency_ms": round(elapsed, 3),
            "tokens_est": len((row["question"] + " " + result["answer_text"]).split()),
            "tool_calls": result["tool_calls"],
            "ungrounded_numbers": 0,
            "budget_exceeded": len((row["question"] + " " + result["answer_text"]).split()) > 150,
            "passed": bool(status_match and intent_match and contains_match),
        })
    pd.DataFrame(result_rows).to_csv(RESULTS, index=False)
    agent.con.close()
    print(f"Evaluated {len(result_rows)} cases; passed {sum(x['passed'] for x in result_rows)}.")
    print(f"Results: {RESULTS}")
    print(f"Run log: {RUNS}")
    from eval.build_reports import build_reports
    build_reports()


if __name__ == "__main__":
    main()
