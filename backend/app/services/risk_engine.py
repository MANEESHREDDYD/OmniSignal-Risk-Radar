from __future__ import annotations

from typing import Any


def score_risk(text: str, sender: str = "", category: str = "") -> tuple[int, list[dict[str, Any]]]:
    text = text.lower()
    sender = sender.lower()
    score = 0
    reasons: list[dict[str, Any]] = []

    def add(code: str, points: int, explanation: str, kind: str = "risk"):
        nonlocal score
        if not any(r["reason_code"] == code for r in reasons):
            score += points
            reasons.append({"reason_code": code, "reason_type": kind, "points": points, "explanation": explanation})

    if any(k in text for k in ["security alert", "unknown device", "secure your account", "suspicious login"]):
        add("security_alert", 45, "Possible unauthorized account access or a security incident was detected.", "security_signal")
    if any(k in text for k in ["payment failed", "card was used", "transaction", "invoice overdue", "fraud"]):
        add("financial_risk", 40, "The message describes potential financial loss or a failed payment.")
    if any(k in text for k in ["legal", "immigration", "visa", "compliance", "international student"]):
        add("legal_or_compliance", 35, "Legal, immigration, school, or compliance language raises consequence risk.")
    if "failure to" in text or "may delay" in text or "penalty" in text:
        add("deadline_consequence", 35, "Missing the stated deadline may have an explicit consequence.")
    if category == "calendar_conflict" or ("calendar" in text and "conflict" in text):
        add("calendar_conflict", 30, "Two calendar commitments appear to overlap.")
    if any(k in text for k in ["timezone", "time zone", "sf time", "your time"]):
        add("timezone_unclear", 25, "The meeting time zone is missing or ambiguous.", "calendar_signal")
    if any(k in text for k in ["in person", "unless you are in", "which office", "location tbd"]):
        add("location_ambiguous", 20, "In-person or remote meeting logistics are not settled.", "calendar_signal")
    if category in {"recruiter", "customer_vip"} or any(k in sender for k in ["recruit", "investor", "customer", "founder"]):
        code = "recruiter_sender" if "recruit" in sender or category == "recruiter" else "vip_sender"
        add(code, 20, "The sender is in a high-value relationship category.", "sender_importance")
    if any(k in text for k in ["send documents", "submit documents", "upload", "send me the deck"]):
        add("document_request", 15, "The sender requests a document or attachment.")
    if any(k in text for k in ["disappointed", "frustrated", "third time", "still waiting"]):
        add("negative_sentiment", 15, "The language suggests frustration or relationship risk.")
    if "http://" in text and sender in {"unknown", ""}:
        add("suspicious_link", 30, "An unknown sender included a non-secure link.")
    if "$" in text and any(k in text for k in ["card", "transaction", "charged"]):
        add("large_amount", 15, "A monetary amount is associated with a financial alert.")
    return min(score, 100), reasons

