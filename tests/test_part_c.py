"""Acceptance checks A01-A20. Run from the project root."""
import json, os, tempfile
from pathlib import Path
from agent.run_agent import Agent

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LOG = Path(tempfile.mkdtemp()) / "runs.jsonl"
agent = Agent(data_dir=str(DATA), log_path=str(LOG))

cases = [
("A01","What was Pune's revenue on 15 May 2026?","Answered","INR 623845.00","s1"),
("A02","And the target?","Answered","Pune, 2026-05-15","s1"),
("A03","How about Mumbai?","Answered","Mumbai, 2026-05-15","s1"),
("A04","How is Hyderabad doing?","Clarification Needed","metric","s2"),
("A05","revenue on 2026-05-15","Answered","Hyderabad","s2"),
("A06","What was Hydrabad's turnover yesterday?","Answered","2026-06-29","s3"),
("A07","Did Pune hit its target on 2026-05-16?","Drafted","74.59%","s4"),
("A08","Did Pune hit its target on 2026-05-20?","Answered","75.30%","s4"),
("A09","Did Mumbai hit its target on 2026-05-21?","Answered","107.99%","s4"),
("A10","Which store had the highest average revenue between 2026-05-01 and 2026-05-31?","Answered","Mumbai INR 1071614.03","s5"),
("A11","Which store had the lowest revenue on 2026-06-10?","Answered","Pune INR 602942.85","s5"),
("A12","Which stores are below the reorder threshold for Amul Milk?","Answered","Hyderabad: 40 units","s6"),
("A13","What are customers saying about Hyderabad?","Answered","average rating 2.63","s6"),
("A14","What was Pune's profit margin on 2026-05-15?","Safe Failure","not in the approved","s7"),
("A15","What is the capital of India?","Escalated","outside","s8"),
("A16","What was Mumbai's revenue on 2026-07-15?","Safe Failure","2026-04-01 to 2026-06-29","s9"),
("A17","Why is Pune's revenue so low?","Escalated","analyst","s10"),
("A18","What was Kolkata's revenue on 2026-05-15?","Clarification Needed","Mumbai, Pune, Hyderabad, Bengaluru, or Ahmedabad","s11"),
("A19","What was Pune's revenue on 15 May 2026?","Answered","INR 623845.00","s12"),
("A20","What was Pune's revenue on 15 May 2026?","Escalated","three attempts","s13"),
]
for cid,q,status,contains,sid in cases:
    result = agent.handle(q,session_id=sid,simulate_failures=2 if cid=="A19" else 3 if cid=="A20" else 0)
    assert result["final_status"] == status, (cid,result)
    assert contains.lower() in result["answer_text"].lower(), (cid,result["answer_text"])
records=[json.loads(x) for x in LOG.read_text(encoding="utf-8").splitlines()]
assert len(records)==20
required={"run_id","user_id","session_id","timestamp","question","intent","confidence","route","executed","attempts","tools_called","status","answer_text","evidence","grounded_values","latency_ms","tokens_est","tool_calls","ungrounded_numbers","budget_exceeded"}
assert all(required.issubset(r) and r["ungrounded_numbers"]==0 for r in records)
print("PASS: 20 Part C acceptance cases and required audit-log schema.")
