# Contributing

Thank you for improving OmniSignal Risk Radar.

## Local Setup

1. Install Python 3.11 or newer and Node.js 22 or newer.
2. Install backend dependencies from `backend/requirements.txt`.
3. Install frontend dependencies with `npm install` inside `frontend`.
4. Keep `DEMO_MODE=true`; do not introduce real credentials or private messages.

## Before Submitting Changes

Run from the repository root:

```bash
make backend-test
make frontend-build
make audit
make eval
make smoke
```

Windows contributors without `make` can follow `scripts/verify_frontend.md` and use the Python verification scripts.

## Product Safety

- Use synthetic fixtures only.
- Never commit secrets, OAuth tokens, or local databases.
- Preserve explainable deterministic reasons.
- Add tests for scoring or routing changes.
- Document any new connector's consent and privacy boundary.

