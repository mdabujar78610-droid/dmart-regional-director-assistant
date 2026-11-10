"""Grounded answer formatting helpers."""
from decimal import Decimal, ROUND_HALF_UP

STATUSES = {"Answered", "Drafted", "Clarification Needed", "Escalated", "Safe Failure"}

def round2(value):
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

def money(value):
    return f"INR {round2(value):.2f}"

def answer_result(status, text, grounded=None, evidence=None, calculation=None, limitations=None):
    if status not in STATUSES:
        raise ValueError(f"Invalid final status: {status}")
    return {
        "status": status,
        "answer_text": text,
        "grounded_values": grounded or {},
        "evidence": evidence or [],
        "calculation_method": calculation or "Direct retrieval from approved source fields",
        "limitations": limitations or [],
    }
