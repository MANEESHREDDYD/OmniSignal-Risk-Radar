# OmniSignal Risk Radar

OmniSignal Risk Radar is a local-first, cross-platform message intelligence layer for AI secretary products. It ingests messages from multiple synthetic accounts, normalizes them into a unified inbox, detects urgency, consequence risk, and action-needed signals, then routes important items to notifications, human triage, or scheduling review.

The V1.1 Google connector foundation is published, and V1.1.1 hardens its
local safety boundaries. The synthetic demo remains fully local,
deterministic, explainable, and usable without real inbox access or paid
services.

## Release Status

- **V1.0:** synthetic multi-account Risk Radar, complete.
- **V1.1:** optional read-only Google connector foundation, published.
- **V1.1.1:** reseed isolation, token refresh, scoped provider IDs, expiring
  OAuth state, local `.env` loading, and stronger guard smoke tests.
- **V1.2:** ActionBridge scheduling actions, planned separately. Incomplete WIP
  is not part of `main`.

## Demo Value

AI secretary products such as Howie are most useful when they protect the user's attention, not merely manage a calendar. OmniSignal demonstrates how an assistant can monitor many communication channels, surface a security alert or deadline before it is missed, suppress newsletter noise, and explain exactly why an interruption was created.

The demo shows a credible path from "assistant that reacts when asked" to "trusted attention layer that notices what matters."

## How This Extends SecretaryOps / TrustOps

SecretaryOps already covers scheduling, reminders, follow-ups, suggested replies, and human review. OmniSignal extends that operating model upstream:

- SecretaryOps receives normalized, prioritized messages instead of raw inbox noise.
- TrustOps receives ambiguous scheduling and calendar-conflict cases for safe human review.
- User actions such as snooze, resolve, task creation, and scheduling handoff are recorded in the audit log.
- Analytics and evaluation provide evidence that the system is catching urgent items without over-alerting.

OmniSignal is therefore a module inside the broader AI secretary system, not a separate inbox product.

## Zero-Budget Design

- No paid APIs or hosted model subscriptions.
- No OpenAI, Anthropic, Twilio, Slack, Teams, Gmail, or Microsoft Graph credentials.
- No connection to real inboxes, SMS accounts, calendars, or private messages.
- No outbound email, SMS, or push notifications.
- Synthetic demo data only.
- SQLite local persistence.
- Deterministic rules and explainable scoring.
- In-app notifications only.

## Architecture

```mermaid
flowchart TD
    A[Connected Accounts / Demo Sources] --> B[Ingestion Service]
    B --> C[Message Normalizer]
    C --> D[Threading + Deduplication Engine]
    D --> E[Entity Extractor]
    E --> F[Urgency Classifier]
    E --> G[Risk Classifier]
    E --> H[Action Needed Detector]
    F --> I[Priority Scoring Engine]
    G --> I
    H --> I
    I --> J{Notification Decision}

    J -->|P0 Immediate| K[Notify Now]
    J -->|P1 Today| L[Today Queue]
    J -->|P2 Digest| M[Daily Digest]
    J -->|P3 Low| N[Archive / Ignore]

    K --> O[Notification Center]
    L --> O
    M --> O
    O --> P[Triage Workspace]
    P --> Q[User Action / Dismiss / Snooze]
    Q --> R[Audit Log]
    Q --> S[Analytics Dashboard]
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the complete system design.

## Features

- Six synthetic accounts: personal Gmail, work Gmail, school Outlook, SMS, iMessage, and calendar.
- 80 demo messages across scheduling, recruiting, interviews, security, finance, official deadlines, VIP follow-ups, conflicts, and newsletters.
- Connector registry and platform-independent normalized message model.
- Cross-platform threading and deterministic deduplication.
- Entity extraction for dates, times, money, deadlines, security events, payment events, document requests, and scheduling language.
- Separate 0-100 urgency, risk, and action-needed scores.
- Weighted P0/P1/P2/P3 priority classification with safety overrides.
- Explainable risk reasons attached to every assessment.
- In-app notification center with snooze, dismiss, and resolve actions.
- Unified inbox, Risk Radar, triage workspace, rules, analytics, and audit log.
- TrustOps scheduling-review handoff.
- Evaluation harness and automated backend tests.

## Screenshots

| View | Screenshot |
| --- | --- |
| Connections | [Six synthetic accounts](docs/screenshots/connections.png) |
| Unified Inbox | [Cross-platform inbox](docs/screenshots/inbox.png) |
| Risk Radar | [Executive risk dashboard](docs/screenshots/radar.png) |
| Notifications | [Priority notification center](docs/screenshots/notifications.png) |
| Triage | [Explainable message assessment](docs/screenshots/triage-security-alert.png) |
| Analytics | [Evaluation and distribution metrics](docs/screenshots/analytics.png) |
| Audit Log | [Decision traceability](docs/screenshots/audit-log.png) |
| Integrations (V1.1) | [Real Google connector, disabled by default](docs/screenshots/integrations-google-disabled.png) |

## Run Locally

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`, with interactive documentation at `http://localhost:8000/docs`.

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

### Docker

```bash
docker compose up --build
```

## Verification

From the repository root:

```bash
make backend-test
make frontend-build
make audit
make eval
make smoke
```

Windows users without `make` can use the commands in [scripts/verify_frontend.md](scripts/verify_frontend.md) and run:

```powershell
python scripts/verify_backend.py
python scripts/run_evaluation.py
python scripts/smoke_test.py
```

Release evidence is captured in [docs/evidence](docs/evidence/).

## Deterministic Scoring

The baseline score is:

```text
priority = round(urgency * 0.40 + risk * 0.35 + action * 0.25)
```

Safety overrides raise security incidents, likely card fraud, actionable same-day deadlines, near-term official document deadlines, scheduling ambiguity, and calendar conflicts to an appropriate minimum tier. Newsletter detection suppresses bulk-mail noise unless a genuine security, finance, or deadline signal is present.

## Demo Walkthrough

Use [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) for a guided product demonstration covering account connections, P0 filtering, security and interview alerts, TrustOps scheduling handoff, notification actions, audit evidence, and evaluation metrics.

## Security and Privacy

- `DEMO_MODE=true` by default.
- No secrets or real credentials are stored.
- Synthetic identities and account addresses are used throughout.
- SQLite stays local and is excluded from version control.
- No messages leave the application.
- Every system and user decision is auditable.

See [docs/evidence/SECURITY_PRIVACY_NOTES.md](docs/evidence/SECURITY_PRIVACY_NOTES.md).

## V1.1 Real Connector Foundation (Optional, Read-Only)

V1.1 adds a safe, opt-in foundation for real **Gmail** and **Google Calendar**
**read-only** access. **Synthetic demo mode remains the default and works with no
setup.** Real sync never runs unless you explicitly enable it.

Safety model:

- `DEMO_MODE=true` and `REAL_CONNECTORS_ENABLED=false` by default.
- All real OAuth and real sync endpoints are guarded — when disabled they return
  a safe, audited "blocked" response and never crash the app.
- Only the required read-only Google scopes are requested:
  `gmail.readonly` and `calendar.events.readonly`.
- The app never sends email, never writes/deletes calendar events, never forwards
  or exports messages, and never downloads attachments.
- OAuth tokens are **encrypted at rest** (Fernet) with a local
  `TOKEN_ENCRYPTION_KEY` and are never returned to the frontend or logged.
- You can **disconnect** an account and **delete the local cache** of synced real
  data at any time, without touching synthetic demo data.
- The local iMessage connector remains synthetic only; no real iMessage access is
  added in this phase.

Real synced messages flow through the same scoring/notification pipeline and
appear in the unified inbox and radar with a small **Real** badge.

### Enable locally (optional)

1. Copy `.env.example` to `.env`. In local development, the backend loads the
   repo-root `.env` or `backend/.env` automatically without overriding variables
   already supplied by the shell.
2. Set `REAL_CONNECTORS_ENABLED=true`.
3. Add `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and a `GOOGLE_REDIRECT_URI` of
   `http://localhost:8000/api/auth/google/callback`.
4. Generate a token key and set `TOKEN_ENCRYPTION_KEY`:
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
5. Open **Settings → Integrations**, connect Google, then run a read-only sync.

Full instructions, including Google Cloud setup and troubleshooting, are in
[docs/REAL_CONNECTOR_SETUP.md](docs/REAL_CONNECTOR_SETUP.md).

The current SQLite schema lifecycle is documented in
[docs/MIGRATION_NOTES.md](docs/MIGRATION_NOTES.md). Hosted multi-user deployment
requires a migration system such as Alembic.

### Git push discipline

Never commit `.env`, local `*.db`/`*.sqlite` files, OAuth tokens, the
`TOKEN_ENCRYPTION_KEY`, or any real message content. These are all covered by
`.gitignore`. Before every push: run the verification suite, `git status`, and
`git diff --staged` to confirm no secrets or local data are staged.

## Future Integrations

| Platform | Future connector |
| --- | --- |
| Gmail | Read-only OAuth foundation complete in V1.1 |
| Outlook | Microsoft Graph API |
| SMS | User-approved phone sync or SMS provider |
| iMessage | Local macOS bridge, subject to Apple platform constraints |
| Slack | Slack App OAuth |
| Teams | Microsoft Graph / Teams APIs |
| Calendar | Google read-only foundation complete; Microsoft Calendar planned |

Real connectors remain disabled by default. See [docs/ROADMAP.md](docs/ROADMAP.md)
for V1.1.1 hardening and the separate V1.2 ActionBridge plan.

## License

Released under the [MIT License](LICENSE).
