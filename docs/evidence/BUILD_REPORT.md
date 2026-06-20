# Frontend Build Report

Validation date: June 20, 2026  
Environment: Windows, Node.js 25.6.0, Next.js 16.2.9

## Command

Canonical command:

```bash
cd frontend
npm run build
```

The Windows validation machine blocks the `npm.ps1` shim through its PowerShell execution policy, so the equivalent native command was run:

```powershell
Set-Location frontend
npm.cmd run build
```

## Result

```text
> omnisignal-risk-radar@1.0.0 build
> next build

Next.js 16.2.9 (Turbopack)
Compiled successfully
TypeScript finished successfully
Generated static pages (11/11)
Finalized page optimization
```

Validated routes:

```text
/
/analytics
/audit-log
/connections
/inbox
/notifications
/radar
/rules
/triage
/triage/[messageId]
```

Status: **PASSED**

## Product Evidence

Seven production-rendered screenshots were captured under `docs/screenshots/` after the build:

- `connections.png`
- `inbox.png`
- `radar.png`
- `notifications.png`
- `triage-security-alert.png`
- `analytics.png`
- `audit-log.png`

