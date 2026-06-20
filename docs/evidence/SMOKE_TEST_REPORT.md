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

## V1.1 Re-validation

Date: June 20, 2026.

During this run, ports `8000` and `3000` were already occupied by pre-existing
local dev servers that the automation did not start and was not permitted to
terminate. The canonical `scripts/smoke_test.py` is hardcoded to those ports, so
an **equivalent end-to-end harness was run on free ports** (backend `8077`,
frontend `3077`, `FRONTEND_ORIGIN` set accordingly) using the same real
subprocesses, real HTTP, and real CORS checks, plus the new V1.1 safety
assertions.

Result:

```text
Backend health: PASSED
Frontend HTTP 200: PASSED
Browser CORS policy: PASSED
80-message / 6-account summary: PASSED
Notification mutation: PASSED
Audit-log mutation evidence: PASSED
Google status safe (disabled, no secrets): PASSED
Real OAuth start blocked when disabled: PASSED
Real sync runs endpoint available: PASSED
Smoke test: PASSED
```

Status: **PASSED**

Additional V1.1 assertions verified: `/api/auth/google/status` reports
`real_connectors_enabled=false` and exposes no tokens or client secret;
`/api/auth/google/start` returns `blocked_disabled` while disabled;
`/api/real-sync/runs` is available; the existing 80-message / 6-account demo is
unaffected. To run the canonical script verbatim, ensure ports 8000/3000 are free.

