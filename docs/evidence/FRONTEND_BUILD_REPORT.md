# Frontend Build Report (V1.1.2)

Date: June 21, 2026
Environment: Windows, Next.js 16.2.9

## Production build

```powershell
cd frontend
npm run build
```

```text
omnisignal-risk-radar@1.1.2 build
Compiled successfully in 3.1s
Finished TypeScript in 2.5s
Generated static pages (12/12)
```

Routes include `/settings/integrations` and dynamic `/triage/[messageId]`.

Status: **PASSED**

## Dependency audit

```powershell
npm audit --audit-level=moderate
```

```text
found 0 vulnerabilities
```

Status: **PASSED**

## Important notes

- The notification badge uses the live unresolved local-notification count with
  a zero fallback.
- Connector and demo status language is dynamic.
- Screenshots contain only synthetic fixture data.
