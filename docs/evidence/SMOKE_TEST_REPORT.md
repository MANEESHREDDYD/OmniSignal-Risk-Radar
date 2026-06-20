# Frontend / Backend Smoke Test Report

Validation date: June 20, 2026  
Execution mode: local production frontend plus FastAPI backend

## Command

Run from the repository root:

```bash
python scripts/smoke_test.py
```

## Result

```text
Backend health: PASSED
Frontend HTTP 200: PASSED
Browser CORS policy: PASSED
80-message / 6-account summary: PASSED
Notification mutation: PASSED
Audit-log mutation evidence: PASSED
Smoke test: PASSED
```

Status: **PASSED**

## Assertions

The smoke script:

1. Starts FastAPI on `127.0.0.1:8000`.
2. Starts the production Next.js build on `127.0.0.1:3000`.
3. Waits for both services.
4. Verifies backend health.
5. Verifies frontend HTTP 200 and rendered OmniSignal content.
6. Verifies the browser origin is accepted by the CORS policy.
7. Verifies 80 analyzed messages and six connected accounts.
8. Snoozes one notification.
9. Confirms the mutation appears in the audit log.
10. Restores the deterministic demo seed.
11. Stops both local processes.

