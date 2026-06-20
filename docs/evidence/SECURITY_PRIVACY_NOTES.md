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

## Production Integration Requirements

Before real connectors are enabled, the project requires scoped OAuth consent, encrypted token storage, revocation, retention limits, redaction, provider rate-limit handling, and a formal outbound-action approval boundary.
