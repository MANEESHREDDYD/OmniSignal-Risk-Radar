# Security and Privacy Notes

Validation date: June 20, 2026.

## V1.0 Data Boundary

- Synthetic demo messages only.
- No real Gmail, Outlook, SMS, iMessage, Slack, Teams, or calendar access.
- No OAuth flow is enabled.
- No API secrets are required.
- No outbound email, SMS, calendar update, or push notification.
- Notifications exist only inside the local application.

## Storage

- SQLite is local to the backend workspace.
- Database files are excluded by `.gitignore`.
- Seed fixtures use fictional identifiers.
- Audit events record product actions without exposing external credentials.

## Configuration

The root `.env.example` documents safe local defaults:

```text
DEMO_MODE=true
DATABASE_URL=sqlite:///./backend/omnisignal.db
FRONTEND_ORIGIN=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

`.env` and `.env.*` files are ignored, except for committed `.env.example` templates.

## Dependency Audit

Canonical command:

```bash
cd frontend
npm audit --audit-level=moderate
```

The Windows validation machine used the equivalent native executable:

```powershell
Set-Location frontend
npm.cmd audit --audit-level=moderate
```

Verified result on June 20, 2026:

```text
found 0 vulnerabilities
```

Status: **PASSED**

## V1.1 Real Connector Safety Model

V1.1 adds an opt-in, read-only Google connector foundation. The default posture
is unchanged: `DEMO_MODE=true`, `REAL_CONNECTORS_ENABLED=false`.

- **Disabled by default.** All real OAuth and real sync endpoints are wrapped by
  a guard (`real_connector_guard.py`). When `REAL_CONNECTORS_ENABLED` is not
  `true`, they return a safe, audited `blocked_disabled` response and never run
  provider code or crash the app. The status endpoint stays available.
- **Read-only scopes only.** `gmail.readonly` and `calendar.events.readonly`
  (optional `calendar.calendarlist.readonly`). No Gmail modify/send scopes; no
  Calendar write scopes.
- **No outbound actions.** The connectors and routers contain no code paths to
  send email, modify/label/delete Gmail messages, create/update/delete calendar
  events, send RSVPs, forward, export, or download attachments. Bodies are
  truncated to a safe size on ingest.
- **Token encryption at rest.** OAuth tokens are encrypted with Fernet using a
  local `TOKEN_ENCRYPTION_KEY` (`token_crypto.py`, `oauth_token_service.py`).
  Plaintext tokens are never persisted, never logged, and never returned to the
  frontend. If the key is missing while real connectors are enabled, token
  storage is blocked with a clear error and the app stays in demo mode.
- **Disconnect and delete cache.** Disconnect deletes stored tokens and marks the
  connection disconnected. Delete-cache removes only this connection's synced real
  records (tracked in `real_synced_items`), never synthetic demo data.
- **Auditability.** OAuth connect, sync, ingestion, disconnect, token deletion,
  cache deletion, blocked attempts, and sync failures are all written to the
  audit log without exposing secrets.
- **iMessage.** No real iMessage connector is added; it remains synthetic.

### Secrets hygiene

`.gitignore` excludes `.env`, `.env.*` (except `.env.example`), all `*.db` /
`*.sqlite` files, and build/test artifacts. `GOOGLE_CLIENT_SECRET`,
`TOKEN_ENCRYPTION_KEY`, access tokens, and refresh tokens must never be committed.

## Production Integration Requirements

Before real connectors are enabled at scale, the project additionally requires
token refresh/revocation hardening, retention limits, redaction policy, provider
rate-limit handling, and a formal outbound-action approval boundary.
