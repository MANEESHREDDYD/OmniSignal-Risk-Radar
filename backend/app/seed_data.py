from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEMO_ACCOUNTS = [
    {"id": "acct_gmail_personal", "user_id": "user_001", "platform": "gmail", "account_label": "Personal Gmail", "account_identifier": "maneesh.personal@example.com", "connection_status": "connected", "is_demo": True},
    {"id": "acct_gmail_work", "user_id": "user_001", "platform": "gmail", "account_label": "Work Gmail", "account_identifier": "maneesh.work@example.com", "connection_status": "connected", "is_demo": True},
    {"id": "acct_outlook_school", "user_id": "user_001", "platform": "outlook", "account_label": "School Outlook", "account_identifier": "maneesh.school@example.edu", "connection_status": "connected", "is_demo": True},
    {"id": "acct_sms", "user_id": "user_001", "platform": "sms", "account_label": "Phone SMS", "account_identifier": "+1-555-0100", "connection_status": "connected", "is_demo": True},
    {"id": "acct_imessage", "user_id": "user_001", "platform": "imessage", "account_label": "iMessage", "account_identifier": "maneesh@icloud.example", "connection_status": "connected", "is_demo": True},
    {"id": "acct_calendar", "user_id": "user_001", "platform": "calendar", "account_label": "Google Calendar", "account_identifier": "maneesh.calendar@example.com", "connection_status": "connected", "is_demo": True},
]

CATEGORY_SPECS = [
    ("scheduling", 12, "gmail", "acct_gmail_work", "Meeting request for next week", "Hi Maneesh, can we meet Tuesday afternoon? I will be in San Francisco but flexible. Maybe Zoom unless you are in the city. Which time zone should we use?"),
    ("rescheduling", 8, "imessage", "acct_imessage", None, "Can we reschedule and move our call from 2 PM to later? I may need to meet in person, location TBD."),
    ("recruiter", 10, "gmail", "acct_gmail_personal", "Data role — response requested", "Hi Maneesh, I am a recruiter working with a strong data platform team. Are you interested? Please confirm availability for an interview tomorrow."),
    ("interview", 6, "outlook", "acct_outlook_school", "Interview confirmation needed by EOD", "We are ready to move forward with your interview. Please confirm your availability by EOD today so we can lock the panel."),
    ("security", 6, "gmail", "acct_gmail_personal", "Security alert: new sign-in from unknown device", "A new sign-in was detected from an unknown device. If this was not you, secure your account immediately."),
    ("finance", 6, "sms", "acct_sms", None, "BANK ALERT: Your card was used for $842.19. Reply YES if authorized or call support immediately."),
    ("official", 8, "outlook", "acct_outlook_school", "Action required: submit documents before deadline", "International Student Office: Please submit documents by June 21, 2026. Failure to respond before the deadline may delay immigration processing."),
    ("customer_vip", 8, "gmail", "acct_gmail_work", "Urgent: customer launch is blocked", "Our customer launch is blocked and the founder is waiting. Please reply by EOD with an approval or we risk missing the commitment."),
    ("follow_up", 6, "imessage", "acct_imessage", None, "Hey, just following up again for the third time. Can you send me the deck today? I am still waiting."),
    ("calendar_conflict", 4, "calendar", "acct_calendar", "Calendar conflict within 24 hours", "Calendar alert: Tomorrow at 2 PM overlaps with your customer review. Choose which meeting to keep."),
    ("newsletter", 6, "gmail", "acct_gmail_personal", "This week in AI startups", "Tech Weekly newsletter: here are the top AI startup stories. Special offer inside. Unsubscribe at any time."),
]

EXPECTED_BY_CATEGORY = {
    "security": ("P0_IMMEDIATE", "notify_now"),
    "finance": ("P0_IMMEDIATE", "notify_now"),
    "official": ("P0_IMMEDIATE", "notify_now"),
    "interview": ("P0_IMMEDIATE", "notify_now"),
    "customer_vip": ("P0_IMMEDIATE", "notify_now"),
    "scheduling": ("P1_TODAY", "send_to_scheduling_review"),
    "rescheduling": ("P1_TODAY", "send_to_scheduling_review"),
    "calendar_conflict": ("P1_TODAY", "send_to_scheduling_review"),
    "recruiter": ("P1_TODAY", "review_today"),
    "follow_up": ("P1_TODAY", "review_today"),
    "newsletter": ("P2_DIGEST", "add_to_digest"),
}

EXPECTED_REASON_CODES_BY_CATEGORY = {
    "scheduling": ["scheduling_request", "timezone_unclear", "location_ambiguous"],
    "rescheduling": ["reschedule_request", "location_ambiguous"],
    "recruiter": ["recruiter_sender", "confirmation_required", "deadline_tomorrow"],
    "interview": ["confirmation_required", "deadline_today", "interview_soon"],
    "security": ["security_alert", "action_required", "urgent_language"],
    "finance": ["financial_risk", "large_amount", "action_required"],
    "official": ["legal_or_compliance", "document_request", "deadline_consequence"],
    "customer_vip": ["vip_sender", "deadline_today", "action_required"],
    "follow_up": ["repeated_follow_up", "negative_sentiment", "document_request"],
    "calendar_conflict": ["calendar_conflict", "deadline_tomorrow"],
    "newsletter": ["newsletter", "no_action_required"],
}


def get_demo_messages() -> list[dict]:
    base = datetime(2026, 6, 20, 7, 0, tzinfo=timezone(timedelta(hours=-4)))
    messages: list[dict] = []
    index = 1
    for category, count, platform, account_id, subject, body in CATEGORY_SPECS:
        for variant in range(count):
            timestamp = base + timedelta(minutes=index * 9)
            expected_level, expected_action = EXPECTED_BY_CATEGORY[category]
            sender_name = {
                "scheduling": ["Alex Chen", "Priya Nair", "Miguel Santos"][variant % 3],
                "rescheduling": ["Jordan", "Casey", "Taylor"][variant % 3],
                "recruiter": ["Sarah Johnson", "Avery Recruiting", "Nina Patel"][variant % 3],
                "interview": "Hiring Operations",
                "security": "Account Security",
                "finance": "Bank Alert",
                "official": "International Student Office",
                "customer_vip": ["Northstar Customer", "Elena, Founder", "Summit Ventures"][variant % 3],
                "follow_up": ["Jordan", "Sam", "Morgan"][variant % 3],
                "calendar_conflict": "Calendar Assistant",
                "newsletter": "Tech Weekly",
            }[category]
            messages.append(
                {
                    "id": f"msg_{index:03d}",
                    "external_message_id": f"{platform}_{index:03d}",
                    "connected_account_id": account_id,
                    "platform": platform,
                    "sender_name": sender_name,
                    "sender_identifier": f"{category}.{variant + 1}@demo.example" if platform not in {"sms", "imessage"} else f"+1-555-{1000 + index}",
                    "recipient_identifiers": [next(a["account_identifier"] for a in DEMO_ACCOUNTS if a["id"] == account_id)],
                    "subject": subject,
                    "body_text": f"{body} Reference #{variant + 1}.",
                    "sent_at": timestamp.isoformat(),
                    "received_at": (timestamp + timedelta(seconds=30)).isoformat(),
                    "has_attachments": category in {"official", "follow_up"},
                    "is_read": variant % 4 == 0,
                    "category": category,
                    "expected": {
                        "priority_level": expected_level,
                        "recommended_action": expected_action,
                        "reason_codes": EXPECTED_REASON_CODES_BY_CATEGORY[category],
                    },
                }
            )
            index += 1
    assert len(messages) == 80
    return messages


DEFAULT_RULES = [
    ("rule_security", "Security alerts interrupt immediately", "signal", {"reason": "security_alert"}, {"minimum_priority": "P0_IMMEDIATE"}),
    ("rule_finance", "Bank and payment alerts interrupt immediately", "signal", {"reason": "financial_risk"}, {"minimum_priority": "P0_IMMEDIATE"}),
    ("rule_deadline", "Today deadlines interrupt immediately", "signal", {"reason": "deadline_today"}, {"minimum_priority": "P0_IMMEDIATE"}),
    ("rule_recruiter", "Recruiter messages surface today", "sender", {"sender_type": "recruiter"}, {"minimum_priority": "P1_TODAY"}),
    ("rule_official", "School, legal, and immigration surface today", "sender", {"sender_type": "official"}, {"minimum_priority": "P1_TODAY"}),
    ("rule_scheduling", "Ambiguous scheduling enters review", "routing", {"reason": "timezone_unclear"}, {"route": "scheduling_review"}),
    ("rule_newsletter", "Newsletters stay in the digest", "suppression", {"reason": "newsletter"}, {"suppress_to_digest": True}),
]


def export_demo_fixtures(output_dir: Path | None = None) -> Path:
    output_dir = output_dir or Path(__file__).resolve().parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    messages = get_demo_messages()
    files = {
        "seed_connected_accounts.json": DEMO_ACCOUNTS,
        "seed_messages.json": messages,
        "seed_calendar_alerts.json": [item for item in messages if item["platform"] == "calendar"],
        "expected_risk_labels.json": [
            {
                "message_id": item["id"],
                "expected_priority_level": item["expected"]["priority_level"],
                "expected_recommended_action": item["expected"]["recommended_action"],
            }
            for item in messages
        ],
        "expected_notification_labels.json": [
            {
                "message_id": item["id"],
                "notification_route": item["expected"]["recommended_action"],
            }
            for item in messages
        ],
    }
    for name, payload in files.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_dir


if __name__ == "__main__":
    print(export_demo_fixtures())
