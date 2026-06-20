from __future__ import annotations

import re
from typing import Any

MONEY_RE = re.compile(r"\$\s?\d[\d,]*(?:\.\d{2})?")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"https?://[^\s)]+")
TIME_RE = re.compile(r"\b(?:1[0-2]|0?[1-9])(?::[0-5]\d)?\s?(?:am|pm)\b", re.I)
DATE_RE = re.compile(
    r"\b(?:today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
    r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|"
    r"sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{0,2}(?:,\s*\d{4})?\b",
    re.I,
)


def extract_entities(message: dict[str, Any]) -> list[dict[str, Any]]:
    text = f"{message.get('subject') or ''} {message.get('body_text') or ''}"
    lowered = text.lower()
    entities: list[dict[str, Any]] = []

    def add(kind: str, value: str, confidence: float = 0.95):
        if not any(item["entity_type"] == kind and item["entity_value"] == value for item in entities):
            entities.append(
                {
                    "entity_type": kind,
                    "entity_value": value,
                    "normalized_value": value.lower().strip(),
                    "confidence": confidence,
                }
            )

    for value in MONEY_RE.findall(text):
        add("money", value)
    for value in EMAIL_RE.findall(text):
        add("email", value)
    for value in URL_RE.findall(text):
        add("url", value)
    for value in TIME_RE.findall(text):
        add("time", value)
    for value in DATE_RE.findall(text):
        add("date", value)

    groups = {
        "security_event": ["security alert", "new sign-in", "unknown device", "secure your account", "verification code"],
        "payment_event": ["payment failed", "card was used", "transaction", "billing", "invoice overdue", "fraud"],
        "document_request": ["send documents", "submit documents", "upload", "send me the deck", "complete form"],
        "calendar_event": ["meeting", "meet ", "calendar", "reschedule", "move our call", "availability"],
        "visa_immigration": ["immigration", "visa", "international student", "sevis"],
        "interview": ["interview", "recruiter", "hiring manager"],
        "deadline": ["deadline", "by eod", "eod today", "reply by", "due today", "due tomorrow"],
    }
    for kind, keywords in groups.items():
        match = next((word for word in keywords if word in lowered), None)
        if match:
            add(kind, match)
    return entities

