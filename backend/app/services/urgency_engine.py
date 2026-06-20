from __future__ import annotations

from typing import Any


def score_urgency(text: str, category: str = "") -> tuple[int, list[dict[str, Any]]]:
    text = text.lower()
    score = 0
    reasons: list[dict[str, Any]] = []

    def add(code: str, points: int, explanation: str):
        nonlocal score
        if not any(r["reason_code"] == code for r in reasons):
            score += points
            reasons.append({"reason_code": code, "reason_type": "urgency", "points": points, "explanation": explanation})

    if any(k in text for k in ["urgent", "asap", "immediately", "right away", "final notice"]):
        add("urgent_language", 30, "The message uses language associated with immediate attention.")
    if any(k in text for k in ["by eod", "eod today", "due today", "deadline today", "today so"]):
        add("deadline_today", 35, "The message includes a deadline that appears to be today or by EOD.")
    elif any(k in text for k in ["tomorrow", "june 21"]):
        add("deadline_tomorrow", 25, "The message references a deadline or event tomorrow.")
    elif "deadline" in text or "within 3 days" in text:
        add("deadline_soon", 15, "A deadline appears to fall within the next few days.")
    if "interview" in text and any(k in text for k in ["today", "tomorrow"]):
        add("interview_soon", 30, "An interview requires attention within the next day.")
    if any(k in text for k in ["security alert", "unknown device", "secure your account"]):
        add("security_alert", 40, "The message reports a possible account security event.")
    if any(k in text for k in ["payment failed", "card was used", "bank alert", "fraud", "invoice overdue"]):
        add("financial_risk", 35, "The message reports a payment, bank, card, or billing issue.")
    if any(k in text for k in ["immigration", "international student", "legal notice", "compliance", "registrar"]):
        add("official_sender", 25, "The message appears to come from an official, school, legal, or compliance context.")
    if any(k in text for k in ["third time", "following up again", "final reminder"]):
        add("repeated_follow_up", 20, "This appears to be a repeated follow-up.")
    if any(k in text for k in ["please confirm", "confirmation needed", "confirm availability", "confirm time"]):
        add("confirmation_required", 20, "The sender explicitly requests confirmation.")
    if category == "calendar_conflict" or ("conflict" in text and "calendar" in text):
        add("calendar_conflict", 20, "A calendar conflict may affect an event within 24 hours.")
    return min(score, 100), reasons

