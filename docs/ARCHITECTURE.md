# OmniSignal Risk Radar Architecture

## System Overview

OmniSignal Risk Radar is a local-first module for SecretaryOps / TrustOps. Its job is to transform heterogeneous communication events into a ranked, explainable attention queue.

The V1.0 system has four boundaries:

1. **Synthetic source boundary** - six demo accounts expose local fixture messages through connector adapters.
2. **Message intelligence boundary** - normalization, threading, entity extraction, scoring, and routing operate on platform-independent records.
3. **User workflow boundary** - the inbox, notification center, triage workspace, rules, analytics, and audit views expose decisions and user controls.
4. **Evidence boundary** - tests, evaluation fixtures, and audit records prove expected behavior on the synthetic dataset.

## Connector Architecture

All connectors implement the `BaseConnector` contract:

```python
class BaseConnector:
    platform: str

    def sync(self, account_id: str) -> list[dict]:
        raise NotImplementedError

    def normalize(self, raw_message: dict) -> dict:
        raise NotImplementedError
```

V1.0 adapters:

- `DemoGmailConnector`
- `DemoOutlookConnector`
- `DemoSmsConnector`
- `DemoIMessageConnector`
- `DemoCalendarConnector`

The adapters read local synthetic fixtures. A future OAuth connector may replace `sync()` without changing downstream scoring or UI contracts.

## Message Normalization Model

Platform-specific payloads become `UnifiedMessage` records containing:

- Connected account and platform
- Sender and recipient identifiers
- Subject and plain-text body
- Sent and received timestamps
- Attachment and read-state metadata
- Stable cross-platform thread key

The original fixture payload is retained separately in `RawMessage`. This separation preserves source evidence while giving every classifier one consistent input model.

Thread keys use canonicalized subjects and normalized participants. Deterministic similarity checks prevent obvious duplicate copies from becoming multiple alerts.

## Scoring Pipeline

The entity extractor identifies structured clues such as dates, times, money, email addresses, URLs, deadlines, document requests, interviews, calendar events, security events, and payment events.

Three independent engines then score the message:

- **Urgency** - time pressure, imminent events, repeated follow-ups, and explicit urgency.
- **Consequence risk** - security, finance, legal, immigration, compliance, calendar, relationship, and suspicious-link signals.
- **Action needed** - confirmation, replies, calls, documents, scheduling, signatures, forms, payment updates, and account remediation.

The base priority formula is:

```text
priority = round(urgency * 0.40 + risk * 0.35 + action * 0.25)
```

The priority engine maps the result to:

- `P0_IMMEDIATE`
- `P1_TODAY`
- `P2_DIGEST`
- `P3_LOW`

Safety overrides raise known high-consequence cases, including security alerts, likely card fraud, actionable same-day deadlines, near-term official document deadlines, and risky scheduling conflicts. Newsletter detection caps interruption priority unless a genuine high-risk signal is present.

Every detected signal creates a `RiskReason` containing a reason code, reason type, point value, and human-readable explanation.

## Notification Routing

The notification router converts the final assessment into one route:

| Priority | Route |
| --- | --- |
| P0 | Notify now |
| P1 | Review today or scheduling review |
| P2 | Add to digest |
| P3 | Keep quiet in the unified inbox |

Notifications are in-app records only. Users can snooze, dismiss, or resolve them. Each mutation writes an audit event.

## Scheduling TrustOps Handoff

Scheduling messages are not auto-executed when the system detects:

- Time-zone ambiguity
- Location ambiguity
- Rescheduling
- Calendar conflict
- Other underspecified logistics

These messages receive `send_to_scheduling_review` and can be handed to the SecretaryOps / TrustOps review queue. The V1.0 handoff is represented as an auditable local queue action; it does not modify an external calendar.

## Audit Logging

`AuditLog` records:

- Actor
- Action
- Target type and identifier
- Before state
- After state
- Timestamp

System scoring, demo synchronization, notification actions, task creation, safe-marking, and scheduling handoffs are traceable.

## Evaluation Harness

The synthetic dataset contains 80 messages with expected priority and routing labels. The evaluation service compares stored assessments against those labels and reports:

- Priority accuracy
- Action-routing accuracy
- P0 precision
- P0 recall
- Expected-reason recall
- Scheduling-routing accuracy
- Newsletter-suppression accuracy

These metrics measure deterministic behavior on the curated demo set. They are not claims about unobserved production inbox traffic.

## Data Storage

SQLite stores connected accounts, raw and normalized messages, threads, entities, assessments, reasons, notifications, action items, synchronization runs, rules, and audit events.

The database is local, reproducible from fixtures, and excluded from Git.

## Future Real Integrations

Real integrations remain disabled by default.

| Platform | Planned integration boundary |
| --- | --- |
| Gmail | Gmail API OAuth connector |
| Outlook | Microsoft Graph mail connector |
| Calendar | Google Calendar and Microsoft Graph calendar connectors |
| Slack | Slack App OAuth connector |
| Teams | Microsoft Graph / Teams connector |
| SMS | User-approved phone synchronization or SMS provider |
| iMessage | Local macOS bridge subject to Apple constraints |

Production integration work must add consent, scoped OAuth, encryption, retention policy, revocation, rate limits, and provider-specific privacy controls before real messages are processed.

