from __future__ import annotations

from typing import Any


def score_action(text: str, important_sender: bool = False) -> tuple[int, list[dict[str, Any]]]:
    text = text.lower()
    score = 0
    reasons: list[dict[str, Any]] = []

    def add(code: str, points: int, explanation: str):
        nonlocal score
        if not any(r["reason_code"] == code for r in reasons):
            score += points
            reasons.append({"reason_code": code, "reason_type": "action_needed", "points": points, "explanation": explanation})

    if any(k in text for k in ["please confirm", "confirm availability", "confirmation needed", "confirm time"]):
        add("confirmation_required", 30, "The sender explicitly asks for confirmation.")
    if any(k in text for k in ["send documents", "submit documents", "send me the deck", "upload documents"]):
        add("document_request", 35, "Documents or files must be sent or submitted.")
    if any(k in text for k in ["reply by", "respond by"]):
        add("action_required", 35, "The message sets a reply deadline.")
    if any(k in text for k in ["call us", "call support", "call immediately"]):
        add("action_required", 25, "The recipient is asked to make a call.")
    if any(k in text for k in ["reschedule", "move our call"]):
        add("reschedule_request", 25, "An existing meeting needs to be rescheduled.")
    elif any(k in text for k in ["can we meet", "schedule", "availability", "confirm time", "meeting request"]):
        add("scheduling_request", 25, "The message requests scheduling or availability.")
    if any(k in text for k in ["approve", "sign the", "signature required"]):
        add("action_required", 30, "Approval or a signature is requested.")
    if any(k in text for k in ["complete form", "complete the form"]):
        add("action_required", 30, "A form must be completed.")
    if any(k in text for k in ["update payment", "update billing", "payment method"]):
        add("action_required", 35, "Billing or payment details must be updated.")
    if "secure your account" in text:
        add("action_required", 40, "The account may need to be secured immediately.")
    if important_sender and "?" in text:
        add("action_required", 15, "An important sender asked a direct question.")
    return min(score, 100), reasons

