# Product Roadmap

## V1.0 - Complete

- Six synthetic connected accounts
- 80-message deterministic fixture set
- Unified inbox and message normalization
- Urgency, risk, action-needed, and priority scoring
- Explainable reason taxonomy
- Notification routing and user actions
- Simulated scheduling-review marker
- Rules, analytics, and audit log
- Automated tests and evaluation harness
- Local and Docker run paths

## V1.1 - Real Google Connector Foundation - Complete

- Read-only Google OAuth for Gmail (`gmail.readonly`) and Calendar
  (`calendar.events.readonly`).
- `REAL_CONNECTORS_ENABLED=false` by default; all real OAuth/sync endpoints
  guarded with safe, audited blocked responses.
- Encrypted-at-rest OAuth token storage (Fernet) keyed by a local
  `TOKEN_ENCRYPTION_KEY`.
- Read-only Gmail and Calendar connectors with injected/mockable clients.
- Real read-only sync (small batches) through the existing scoring/notification
  pipeline, with `real_sync_runs` tracking and provider cursors.
- Account disconnect and delete-local-cache for synced real data, isolated from
  synthetic demo data.
- Settings → Integrations UI with disabled-by-default state and consent copy.
- Audit logs for connection, sync, ingestion, disconnect, token deletion, cache
  deletion, blocked attempts, and sync failures.
- Mocked tests for OAuth guard, token crypto, token service, connectors, sync
  guard, and cache deletion. No outbound actions of any kind.

## V1.1 Guardrails (enforced)

- Real-account support is opt-in; synthetic demo mode remains the default.
- OAuth tokens are encrypted at rest and never stored in source control.
- No email send, calendar write, message forwarding, or attachment download.
- Outbound messaging remains out of scope behind a separate approval boundary.

## V1.1.1 - Real Connector Hardening - Complete

- Demo force-reseed deletes and restores only synthetic rows while preserving
  OAuth connections, encrypted tokens, cursors, sync runs, and real cache.
- OAuth access-token expiry is stored and expired tokens refresh before sync.
- Refresh failures mark the connection as error and the sync run as failed.
- Gmail and Calendar local resource IDs are scoped per connected Google account.
- Local `.env` loading uses `python-dotenv` with process variables taking
  precedence and safe defaults unchanged.
- Default Google scopes reduced to Gmail read-only and Calendar events read-only.
- OAuth state is single-use and expires after ten minutes.
- Canonical smoke coverage includes disabled Google OAuth/sync guards and
  response secret checks.

## V1.1.2 - Audit Fixes and Product Truth - Complete

- Cache deletion is isolated by OAuth connection and preserves other accounts'
  messages, assessments, notifications, threads, and audit history.
- Evaluation ignores unlabeled provider data and reports labeled/ignored counts.
- Synthetic fixtures include expected reason codes; reason recall is no longer
  vacuous.
- Enabled deterministic sender/keyword rules affect ingestion and reanalysis.
- Scheduling handoff language now describes the implemented simulated marker.
- Active cross-platform deduplication is explicitly not claimed.
- Google live sync remains unvalidated.

## V1.2 - OmniSignal Command Center and Daily Briefs (planned)

- Local action cards, deterministic assistant-style queries, daily briefings,
  user-readable daily logs, and simulated reply approval.
- No real send or Calendar write until a separate approval-gated production
  boundary is designed and verified.
- Alembic migration infrastructure should be introduced before hosted or
  multi-user deployment.

## V1.3 - Microsoft Graph (planned)

- Read-only Outlook mail and Microsoft Calendar via Microsoft Graph OAuth.
- Local LLM second-opinion adapter, disabled by default.
- Review correction feedback loop and configurable digest generation.
- Notification fatigue controls and priority calibration dashboard.

## V1.4 - Local iMessage Bridge (planned, later)

- Local macOS iMessage bridge, subject to Apple platform constraints.
- Remains synthetic-only until then; no real iMessage access before V1.4.

## Later Opportunities

- Multi-user SecretaryOps workspaces
- Organization-specific VIP and compliance policies
- Encrypted local message cache
- Calibrated confidence and abstention behavior
- Time-based notification budgets
- Provider health and connector observability
- Human-reviewed suggested replies
