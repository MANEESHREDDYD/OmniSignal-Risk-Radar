# Frontend Build Report (V1.1)

Date: June 20, 2026
Environment: Windows 11, Node + Next.js 16.2.9

## Command

Run from the `frontend` directory:

```bash
npm run build
```

## Result

```text
✓ Compiled successfully in 13.6s
  Finished TypeScript in 3.0s
✓ Generating static pages (12/12)

Route (app)
┌ ○ /
├ ○ /analytics
├ ○ /audit-log
├ ○ /connections
├ ○ /inbox
├ ○ /notifications
├ ○ /radar
├ ○ /rules
├ ○ /settings/integrations   <-- new in V1.1
├ ○ /triage
└ ƒ /triage/[messageId]
```

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

- New route `/settings/integrations` builds and prerenders successfully.
- Added a non-blocking **Real** badge in the message table for real (non-demo)
  messages.
- No new runtime dependencies were added to the frontend.
