# Frontend Build Report (V1.1.1)

Date: June 20, 2026
Environment: Windows 11, Next.js 16.2.9

## Production build

```bash
cd frontend
npm run build
```

```text
omnisignal-risk-radar@1.1.1 build
Compiled successfully in 2.8s
Finished TypeScript in 3.2s
Generated static pages (12/12)
```

Routes include `/settings/integrations` and dynamic `/triage/[messageId]`.

Status: **PASSED**

## Dependency audit

```bash
npm audit --audit-level=moderate
```

```text
found 0 vulnerabilities
```

Status: **PASSED**

## Notes

- Global navigation now reports demo-account count, real-connector enabled
  state, and connected real-account count dynamically.
- No Google token or client-secret value is rendered by the frontend.
