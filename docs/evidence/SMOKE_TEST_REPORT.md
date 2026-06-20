# Frontend / Backend Smoke Test Report (V1.1.1)

Date: June 20, 2026
Execution mode: production Next.js frontend plus FastAPI backend

## Command

```bash
python scripts/smoke_test.py
```

The script uses ports `8000` and `3000` when available and automatically
chooses free local ports otherwise. Ports can also be supplied with
`OMNISIGNAL_BACKEND_PORT` and `OMNISIGNAL_FRONTEND_PORT`.

## Result

```text
Backend health: PASSED
Frontend HTTP 200: PASSED
Browser CORS policy: PASSED
80-message / 6-account summary: PASSED
Google status safe while disabled: PASSED
OAuth start blocked while disabled: PASSED
Real sync blocked while disabled: PASSED
No connector secrets in responses: PASSED
Notification mutation: PASSED
Audit-log mutation evidence: PASSED
Smoke test: PASSED
```

Status: **PASSED**

## Important notes

- The smoke process explicitly forces `DEMO_MODE=true` and
  `REAL_CONNECTORS_ENABLED=false`.
- The final demo reseed preserves any real OAuth/token/sync state by deleting
  and restoring demo rows only.
- No real Google provider request is made.
