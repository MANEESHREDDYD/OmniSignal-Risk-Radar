# Frontend Verification on Windows

Run these commands from PowerShell.

## Production Build

```powershell
Set-Location frontend
npm.cmd install
npm.cmd run build
```

Expected result: Next.js completes the optimized production build and lists all application routes.

## Dependency Audit

```powershell
npm.cmd audit --audit-level=moderate
```

Expected result:

```text
found 0 vulnerabilities
```

## Return to the Repository Root

```powershell
Set-Location ..
python scripts/smoke_test.py
```

Expected result: backend health, frontend HTTP response, demo-data summary, notification mutation, and audit evidence all pass.
