# Brutal Product Audit: OmniSignal Risk Radar

> Historical audit note: this report evaluates commit `27e2b3d` before the
> V1.1.2 audit-fix pass. Findings are preserved as the evidence that motivated
> the subsequent fixes.

Audit date: June 21, 2026
Audited commit: `27e2b3d5b8aec2088fb40154ca84a6802bede3f6`
Repository: <https://github.com/MANEESHREDDYD/OmniSignal-Risk-Radar>
Local branch: `main`

## Executive Summary

OmniSignal Risk Radar is a polished local demo of a deterministic message-priority dashboard plus an unproven, read-only Google connector foundation.

It is not an AI secretary. It does not use an AI model. It does not schedule meetings, send replies, create drafts, write calendar events, or communicate with anyone. Its core working product is:

1. Seed 80 synthetic messages from 11 repeated scenario templates.
2. Normalize them into a common SQLite schema.
3. Apply English keyword heuristics for urgency, risk, and action-needed scores.
4. Assign P0/P1/P2/P3 labels and in-app routes.
5. Display the results in a polished dashboard.
6. Record local user actions in an audit table.

The Google integration has real OAuth and HTTP code, encrypted token storage, expiry/refresh handling, read-only scopes, and disabled-by-default guards. However, it has only been tested with mocks and blocked smoke flows. No real Google account has been connected in this checkout. Successful end-to-end Gmail or Calendar sync is therefore **not proven**.

The repository is credible as a portfolio prototype if described accurately. It is not credible as a production inbox product or Howie-equivalent assistant.

The most serious findings are:

- There is no authentication or authorization anywhere in the app.
- Real message content would be stored unencrypted in SQLite.
- Delete-cache has a reproduced cross-account thread-deletion bug.
- The evaluation service has a reproduced failure when real raw messages exist.
- “User rules,” deduplication, connector registry behavior, scheduling review, and several UI controls are partially decorative or disconnected from the actual pipeline.
- The 100% evaluation score measures conformity to hand-authored synthetic labels generated beside the same templates used to tune the rules. `reason_recall` is vacuously 100% because no expected reason codes are supplied.
- Screenshots are stale relative to V1.1.1; the Google screenshot still shows a scope that the code removed.

## Audit Method and Verification

The audit inspected all tracked application areas: backend models, routers, services, fixtures, tests, frontend pages/components, docs, evidence reports, screenshots, Docker files, verification scripts, and git metadata.

Commands rerun during this audit:

| Check | Result |
| --- | --- |
| `cd backend && python -m pytest -q` | **73 passed in 1.66s** |
| `cd frontend && npm.cmd run build` | **Passed**, compiled in 2.4s, TypeScript in 2.2s, 12 generated routes |
| `cd frontend && npm.cmd audit --audit-level=moderate` | **0 vulnerabilities** |
| `python scripts/run_evaluation.py` | **Passed**, all reported synthetic metrics `1.0` |
| `python scripts/smoke_test.py` | **Passed**, including disabled Google guards |
| `python -m compileall -q backend/app scripts` | **Passed** |
| Tracked Markdown link check | **Passed** |
| Credential-pattern scan | **No likely committed secrets found** |

Important limitation: `npm audit` checks the Node dependency tree only. No equivalent Python dependency vulnerability scan is configured.

Two additional diagnostics exposed gaps not covered by the suite:

1. Deleting cache for Google account A left account B’s message but deleted account B’s `MessageThread`.
2. Running `run_evaluation()` with a real-style raw message failed with `KeyError` because the evaluator assumes every payload contains synthetic `expected` labels.

## 1. What the Product Actually Is

### What it is today

OmniSignal is a single-user localhost dashboard for demonstrating explainable inbox prioritization across synthetic communication channels. It also contains the foundation of an optional Google read-only connector.

The actual center of gravity is a **risk/priority classification demo**, not a secretary:

- FastAPI reads or seeds message records.
- Deterministic keyword rules assign scores.
- Next.js displays inbox, radar, notification, triage, analytics, and audit views.
- User actions mutate local SQLite records.

### User problem it addresses

It demonstrates a possible answer to: “If messages arrive across several channels, which ones deserve attention first, and why?”

It does not solve the full operational problem of acting on those messages.

### Workflow it supports

The working demo workflow is:

`synthetic fixtures -> normalization -> heuristic scoring -> in-app notification/triage -> local action/audit`

The optional but unproven real workflow is:

`Google OAuth -> read up to 25 Gmail messages / primary-calendar events -> local storage -> same heuristic scoring`

### Product category

| Category | Honest classification |
| --- | --- |
| AI secretary | **No** |
| Inbox triage tool | **Yes, as a local demo** |
| Risk radar | **Yes; this is the best-fitting name** |
| Connector foundation | **Yes, for read-only Google; not live-proven** |
| Scheduling assistant | **No** |
| Scheduling-risk detector | **Partially, through keywords** |
| Production inbox product | **No** |

### Does the name and README match?

“Risk Radar” matches the implemented demo. “OmniSignal” implies live cross-platform coverage that does not exist: Gmail, Outlook, SMS, iMessage, and demo Calendar are synthetic. Only Google has real connector code, and that code has not been live-tested.

The README is strongest when it calls this a “module” or “foundation.” It overreaches when it implies an operational AI secretary layer, real cross-platform monitoring, reliable deduplication, functional user policy, or proven Google integration.

## 2. What the Product Can Actually Do Right Now

Status definitions:

- **Real and working:** exercised against the running local app.
- **Demo-only:** works only with synthetic fixtures/local simulation.
- **Mock-tested only:** provider behavior is represented by fakes.
- **Structurally present, not live-tested:** implementation exists but no real provider proof.
- **Not implemented:** no meaningful code path exists.

### Synthetic/demo capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Seed six demo accounts | **Real and working; demo-only** | `seed.py`, 6 accounts verified |
| Seed 80 messages | **Real and working; demo-only** | 80 records across 11 scenario templates |
| Normalize Gmail/Outlook/SMS/iMessage/Calendar-shaped data | **Real and working; demo-only** | `message_normalizer.py` and tests |
| Score urgency, risk, and action need | **Real and working; demo-only validation** | Keyword engines and tests |
| Assign P0/P1/P2/P3 | **Real and working; demo-only validation** | `priority_engine.py` |
| Create local notifications and action items | **Real and working; demo-only** | Seed and real-ingestion paths |
| Create message threads | **Real and working, limited** | Basic thread keys and thread rows |
| Cross-platform deduplicate messages | **Not implemented in ingestion** | `thread_deduper.py` exists but is unused |
| Demo connector registry | **Structurally present but unused** | `CONNECTORS` exists; sync endpoint does not call it |
| “Sync demo data” | **Demo-only simulation** | Updates timestamp and logs a run; it does not ingest through connectors |

### Real Google connector capabilities

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Report disabled/configured status | **Real and working** | Smoke-tested `/api/auth/google/status` |
| Block OAuth and sync by default | **Real and working** | Guard tests and smoke test |
| Build Google authorization URL | **Mock/config-tested only** | No browser-to-Google live proof |
| Exchange OAuth code | **Structurally present, not live-tested** | `google_oauth.exchange_code()` |
| Encrypt tokens at rest | **Real and working in unit tests** | Fernet round-trip and DB ciphertext tests |
| Refresh expired tokens | **Mock-tested only** | Unit tests; no live refresh |
| Read Gmail message list/details | **Mock-tested only** | Real HTTP GET client exists |
| Read primary Google Calendar events | **Mock-tested only** | Real HTTP GET client exists |
| Successful real Gmail sync route | **Structurally present, not live-tested** | No successful route-level provider test |
| Successful real Calendar sync route | **Structurally present, not live-tested** | No successful route-level provider test |
| Disconnect locally | **Structurally present; token deletion unit-tested** | Does not revoke the Google grant |
| Delete local cache | **Tested for one account, unsafe across accounts** | Reproduced cross-account thread deletion |

### UI capabilities

| Capability | Status |
| --- | --- |
| Command center dashboard | **Real and working** |
| Unified inbox with priority/search filters | **Real and working; synthetic by default** |
| Risk radar and distributions | **Real and working** |
| Notification list and snooze/dismiss/resolve | **Real and working** |
| Triage list/detail | **Real and working** |
| Create local task | **Real and working** |
| Mark safe / resolve related notifications | **Real and working** |
| Integrations disabled-state page | **Real and working** |
| Rules CRUD | **UI/API works; rules do not affect scoring** |
| Audit search | **Not implemented; visual input only** |
| Inbox “Filters” button | **Not implemented; visual button only** |
| Triage-detail Snooze | **Not implemented; button has no handler** |
| Responsive mobile navigation | **Not implemented**; sidebar disappears below `lg` |
| Dynamic notification badge | **Not implemented**; hardcoded `25` |

### Backend/API capabilities

- FastAPI exposes 46 router endpoints plus `/api/health`.
- Read, filter, reanalyze, mutate notifications, create tasks, mutate rules, display analytics, and list audit events all work locally.
- There is no authentication, authorization, tenancy enforcement, pagination for the main inbox, rate limiting, or production session management.

### Scoring and notification capabilities

- Three deterministic keyword engines produce 0–100 scores.
- Weighted priority and explicit override rules are implemented.
- In-app notification records are implemented.
- “Digest” is a route/category, not a generated digest product.
- Real calendar conflict detection is not implemented. The system recognizes the words “calendar” and “conflict”; it does not compare overlapping event intervals.
- Date understanding is not robust. For example, `urgency_engine.py` hardcodes `"june 21"` as “tomorrow.”

### Audit/logging capabilities

- Local mutations and many system operations create `AuditLog` rows.
- The audit log is useful as demo traceability.
- It is not tamper-evident, user-authenticated, or a compliance-grade audit trail.
- Force reseeding preserves old audit rows and adds 80 new “Scored message” rows, causing repeated demo runs to accumulate noisy duplicate audit history.

### Security/privacy capabilities

- Real connectors are disabled by default.
- Google scopes are read-only.
- OAuth tokens are encrypted with a local Fernet key.
- Tokens are not returned by API responses.
- `.env`, databases, dependencies, and build artifacts are ignored.
- No Gmail send/modify or Calendar write provider methods were found.

These are meaningful local safety controls, but they do not make the app safe for production private data.

## 3. What the Product Cannot Do

| Question | Blunt answer |
| --- | --- |
| Connect a real Gmail account end-to-end? | **Not proven.** Code exists; live connection has never been tested here. |
| Connect real Google Calendar end-to-end? | **Not proven.** Same limitation. |
| Sync real Gmail messages? | **Structurally yes, operationally unproven.** Mock-tested only. |
| Sync real Calendar events? | **Structurally yes, operationally unproven.** Mock-tested only. |
| Send emails? | **No.** |
| Create Gmail drafts? | **No.** |
| Write calendar events? | **No.** |
| Schedule meetings? | **No.** |
| Reply to people? | **No.** |
| Book meetings like Howie? | **No.** |
| Connect Outlook/Microsoft 365? | **No.** Outlook is synthetic only. |
| Connect real iMessage? | **No.** |
| Connect Slack or Teams? | **No.** |
| Run as a production SaaS? | **No.** |
| Support multiple users safely? | **No.** User identity is hardcoded as `user_001`; APIs are unauthenticated. |
| Handle real private user data safely today? | **No.** Message bodies, senders, and recipients would be plaintext in SQLite and exposed through unauthenticated APIs. |
| Evaluate performance on real-world email data? | **No.** There is no labeled real dataset; the evaluator currently crashes on real-style raw messages. |

The “TrustOps scheduling review queue” is not a real queue. The endpoint writes an audit entry and returns `{"status":"queued"}` with a string label. There is no scheduling-review model, queue state, assignment workflow, scheduling parser, candidate-slot generation, or scheduling review screen.

## 4. Product Truth vs Pitch

### Claim 1

**Claim:** “Cross-platform message intelligence layer.”

**Reality:** Five platforms are represented by synthetic fixtures. Google Gmail/Calendar have unproven real code. Outlook, SMS, iMessage, Slack, and Teams are not live.

**Risk:** Readers may assume operational cross-platform integrations.

**Fix:** Say “cross-platform synthetic prototype with an optional, unproven Google read-only foundation.”

### Claim 2

**Claim:** “AI secretary products” and “advanced module inside the AI secretary.”

**Reality:** There is no LLM, learned classifier, agent, reply generation, calendar action, or autonomous secretarial workflow.

**Risk:** “AI secretary” sounds like a capability claim rather than target architecture.

**Fix:** Say “deterministic attention-triage prototype intended as upstream infrastructure for a future secretary.”

### Claim 3

**Claim:** “Cross-platform threading and deterministic deduplication.”

**Reality:** Thread keys are generated, but `thread_deduper.is_duplicate()` is never called by seed or real ingestion. Real provider thread keys are account-scoped and not cross-platform.

**Risk:** A core implemented feature is overstated.

**Fix:** Claim “basic thread-key creation”; do not claim active deduplication.

### Claim 4

**Claim:** “Connector registry” and “Sync demo data.”

**Reality:** The demo `CONNECTORS` registry is dead code. `/connections/{id}/sync` only counts existing rows and records a completed sync with zero created messages. It also accepts real account IDs.

**Risk:** The UI presents a sync pipeline that does not run.

**Fix:** Label it “simulate sync status” until the endpoint actually invokes connectors and ingestion.

### Claim 5

**Claim:** “User rules / preferences” shape interruption thresholds.

**Reality:** Rules can be created, toggled, and deleted, but `assess_message()` never reads `UserRule`.

**Risk:** Users believe configuration affects decisions when it does not.

**Fix:** Either wire rules into scoring or label the page a non-functional prototype.

### Claim 6

**Claim:** “TrustOps scheduling-review handoff.”

**Reality:** The handoff is only an audit row and response string. No queue or downstream scheduling system exists.

**Risk:** This sounds like product integration that is not present.

**Fix:** Call it “simulated scheduling-review marker.”

### Claim 7

**Claim:** “100% evaluation” and “Expected-reason recall: 100%.”

**Reality:** The dataset contains 11 repeated semantic templates. Expected priority/action labels are generated next to those templates. No expected reason codes are populated, so `reason_recall` defaults to `1.0` when its denominator is zero.

**Risk:** The metrics appear much more credible than they are.

**Fix:** Remove reason recall until reason labels exist; call all metrics “fixture conformance,” not accuracy.

### Claim 8

**Claim:** “Real synced messages flow through the same analytics/evaluation layer.”

**Reality:** Ingestion and radar can accept real-style records, but `evaluation_service.py` assumes every raw payload has `expected`. A reproduced diagnostic failed with `KeyError`.

**Risk:** Real sync can break the Analytics page’s evaluation request.

**Fix:** Filter evaluation to demo records or use an explicitly selected labeled dataset.

### Claim 9

**Claim:** “Delete local cache removes only this connection’s records.”

**Reality:** Message deletion is connection-scoped, but thread cleanup scans all real-looking threads. A reproduced two-account test deleted account B’s thread while deleting account A.

**Risk:** Cross-account metadata corruption.

**Fix:** Scope thread deletion to thread keys owned by the selected connection.

### Claim 10

**Claim:** “Every system and user decision is auditable.”

**Reality:** Many actions are logged, but not every internal decision has a distinct audit event; actors are hardcoded labels; logs are not authenticated or tamper-resistant.

**Risk:** “Audit” can be mistaken for compliance-grade evidence.

**Fix:** Say “local debugging and traceability log.”

### Claim 11

**Claim:** “Zero-budget design: no Gmail credentials, no connection to real inboxes.”

**Reality:** Later sections explain optional real Gmail/Calendar credentials and access.

**Risk:** The README contradicts itself.

**Fix:** Make the section explicitly “default synthetic demo mode,” not a universal product property.

### Claim 12

**Claim:** Screenshots represent the current product.

**Reality:** Most screenshots show the older sidebar and hardcoded “6 accounts connected” / “Synthetic messages only” text. The integrations screenshot still shows Calendar-list scope, which V1.1.1 removed.

**Risk:** Evidence is stale and internally inconsistent.

**Fix:** Recapture all screenshots from the audited commit.

## 5. How Close Is It to Howie?

Against the Howie-style product description supplied with this repository—scheduling, reminders, follow-ups, and secretary workflows—OmniSignal is **adjacent infrastructure**, not a direct Howie-equivalent feature.

- **Alignment:** Moderate at the problem level. Prioritizing inbound requests could feed a scheduling assistant.
- **Direct Howie feature:** No. It does not parse a scheduling conversation into candidate times, coordinate participants, send a reply, or create an event.
- **Adjacent infrastructure:** Yes. A trusted assistant needs message ingestion, risk controls, triage, and auditability.
- **Would a founder/engineer care?** Possibly as an architectural prototype, but only after the claims are narrowed.

What they would criticize first:

1. No live end-to-end connector proof.
2. No scheduling action loop.
3. No actual AI or language understanding.
4. Synthetic evaluation designed around the heuristics.
5. No authentication or multi-user model.
6. A “review queue” that is just an audit string.

What may impress them:

1. Clear read-only and disabled-by-default safety posture.
2. Explainable deterministic reasons instead of opaque scores.
3. Token encryption and refresh foundation.
4. Polished visual prototype.
5. Good basic test discipline for a portfolio project.
6. Recognition that ambiguous scheduling should require review rather than automatic action.

What must exist before it is truly Howie-aligned:

- Live email/calendar ingestion proven with a controlled account.
- Scheduling intent and thread-state parsing.
- Availability lookup and candidate-slot generation.
- Approval-gated reply/draft generation.
- Calendar event proposal/creation with explicit consent.
- Participant/time-zone handling.
- Real correction feedback and measured outcomes.
- Authentication, tenant isolation, retention, and migrations.

## 6. Technical Architecture Audit

### Backend stack

- Python 3.11
- FastAPI 0.115.12
- SQLAlchemy 2.0
- SQLite
- Pydantic 2
- `httpx`
- Fernet via `cryptography`
- Pytest

The backend is synchronous and small. There are no background jobs, queues, workers, migrations, auth middleware, or async provider clients.

### Frontend stack

- Next.js 16.2.9 App Router
- React 19
- TypeScript
- Tailwind CSS
- Lucide icons
- Client-side data fetching from FastAPI

Most pages are client components. There is no frontend test framework.

### Database design

The schema is broad enough for the demo, with accounts, raw messages, normalized messages, threads, entities, assessments, reasons, notifications, tasks, rules, sync runs, OAuth connections, encrypted tokens, cursors, real sync runs, real-item traceability, and audit logs.

Weaknesses:

- `create_all()` is used instead of migrations.
- Many connector tables do not declare foreign keys.
- No uniqueness constraints protect one token/cursor per connection.
- SQLite foreign-key enforcement is not explicitly enabled.
- Timestamps and statuses are free-form text.
- No ownership checks enforce `user_id`.
- Message content is plaintext.
- Delete behavior is manually coded and error-prone.

### Scoring pipeline

The scoring code is readable and explainable, but it is a brittle English keyword system:

- No semantic model.
- No negation handling.
- No quoted-thread separation.
- No sender authentication.
- No robust date parsing despite dependencies being installed.
- No calibrated confidence.
- No learning from corrections.
- Hardcoded date phrase `"june 21"` is treated as “tomorrow” permanently.

Likely false positives include phishing emails containing “security alert,” historical quoted deadlines, “not urgent,” newsletters discussing fraud, and resolved incidents.

Likely false negatives include indirect asks, polite or terse executive language, non-English mail, HTML-only content beyond the Gmail snippet, complex date expressions, and urgency implied by context rather than keywords.

### Connector architecture

The Google connectors have a good injected-client shape. The demo connector interface is conceptually clean but disconnected from actual demo ingestion. `BaseConnector` and `CONNECTORS` are mostly architectural scaffolding.

The real connector is not incremental:

- Maximum 25 records.
- No Gmail pagination.
- No Calendar pagination.
- `cursor_value` is never populated.
- No Gmail history ID or Calendar sync token.
- No 401-refresh-and-retry path.
- No retry/backoff or quota handling.

### OAuth/security architecture

Good:

- Disabled by default.
- Read-only scopes.
- Encrypted tokens.
- Expiring single-use state.
- Secret-safe error responses.

Fragile:

- OAuth state is global in-memory state, not tied to a browser session or user.
- No PKCE.
- No durable state across restarts/workers.
- Granted scopes are not validated; requested scopes are stored as if granted.
- Disconnect does not revoke the Google token/grant.
- Duplicate connections for the same Google account are possible.
- No auth protects connection IDs or account email status.

### Test architecture

There are 55 test functions producing 73 pytest cases through parametrization.

Strengths:

- Fast tests.
- In-memory DB fixtures for connector tests.
- Good focused checks for disabled guards, encryption, token refresh, account-scoped provider IDs, and demo reseed isolation.

Weaknesses:

- No live Google test.
- No successful route-level Gmail/Calendar sync test.
- No frontend component or browser E2E test.
- No multi-account delete-cache test.
- No evaluation-with-real-data test.
- No transaction rollback/partial-ingestion test.
- No pagination, rate-limit, malformed Calendar conference data, duplicate callback, or token revocation tests.
- No coverage measurement.
- Smoke test checks the home page and a narrow API path, not all UI actions.
- Scoring tests mostly repeat the phrases the implementation explicitly checks.

### Clean areas

- Small service modules with clear names.
- Read-only provider client surface.
- Explicit connector guard.
- Token crypto boundary.
- Account-scoped provider IDs.
- Deterministic behavior that is easy to debug.

### Fragile areas

- Manual cascade deletion.
- Shared global OAuth/evaluation state.
- Partial commits on sync failures: exception handlers commit without rolling back pending ingestion.
- N+1 queries in message serialization.
- Main inbox loads all messages without server pagination.
- Real-thread cleanup bug.
- Real-data evaluator crash.

### Over-engineered areas

- The amount of release/evidence/roadmap documentation exceeds the maturity of the implementation.
- Five real-connector metadata tables exist before one live provider test.
- Several layers are present as architecture theater but are not wired: connector registry, deduper, user rules.

### Under-engineered areas

- Authentication and tenancy.
- Migrations and referential integrity.
- Real data encryption/retention.
- Scheduling workflow.
- Real NLP/evaluation.
- Incremental sync and provider resilience.
- UI behavior and accessibility testing.

### Where real data will break it

1. Evaluation crashes on real raw payloads.
2. Date and urgency heuristics misread normal language.
3. Large inboxes overwhelm unpaginated APIs and N+1 serialization.
4. MIME/address edge cases produce incomplete or malformed messages.
5. Full sync can commit partial Gmail data if Calendar fails.
6. Multi-account cache deletion can corrupt another account’s thread metadata.
7. Real Calendar events are not checked for actual overlaps.

## 7. Real Connector Audit

| Question | Finding |
| --- | --- |
| Disabled by default? | **Yes.** `Settings.REAL_CONNECTORS_ENABLED` defaults false. |
| OAuth routes guarded? | **Yes.** Start, callback, disconnect, delete-cache, and sync call `ensure_google_configured()`. |
| Tokens encrypted? | **Yes.** Fernet in `token_crypto.py`; encrypted columns in `EncryptedToken`. |
| Token refresh implemented? | **Yes, mock-tested.** `get_valid_access_token()` refreshes near expiry. |
| Scopes read-only? | **Yes.** Gmail read-only and Calendar events read-only only. |
| IDs account-scoped? | **Yes.** Gmail and Calendar IDs/external IDs/thread keys include connected-account ID. |
| Delete-cache safe? | **No.** Message deletion is scoped, but cross-account thread deletion was reproduced. |
| Demo reseed preserves real state? | **Yes in current tests** for connection, token, cursor, sync run, real item, account, and message rows. |
| Google calls tested only with mocks? | **Yes.** |

Unproven until a controlled live account test:

- Google consent-screen acceptance.
- Whether requested scopes and user-info lookup behave together.
- Refresh-token issuance and refresh behavior.
- Gmail MIME behavior on real mail.
- API pagination and ordering.
- Calendar all-day, recurring, canceled, private, and malformed events.
- Token expiry under actual provider responses.
- Live quota/error behavior.
- Successful sync through the route into inbox/radar/UI.
- Disconnect/reconnect behavior.
- Google-side token revocation expectations.

The local database at audit time contained:

- 6 accounts
- 80 messages
- 0 OAuth connections
- 0 encrypted tokens
- 0 real synced items
- 4 blocked real-sync run records from guard/smoke checks

That is direct evidence that no real Google account was tested in this checkout.

## 8. Data and Evaluation Audit

### Synthetic data

All 80 message records are synthetic. They come from 11 category templates:

- 12 scheduling
- 8 rescheduling
- 10 recruiter
- 6 interview
- 6 security
- 6 finance
- 8 official/deadline
- 8 customer/VIP
- 6 follow-up
- 4 calendar-conflict
- 6 newsletter

Within each category, messages mostly vary by sender and a “Reference #” suffix. This is not 80 independent linguistic cases.

### Real data

There is no real message data in the audited local DB or repository. Real provider payloads exist only as mocked test fixtures.

### What 100% actually means

It means the deterministic engine reproduces the priority and route labels assigned to its own curated 11-template fixture family.

It does not mean:

- 100% email classification accuracy.
- 100% urgent-message recall in real inboxes.
- 100% false-positive avoidance.
- 100% reason extraction.
- Any measured performance on private or naturally occurring messages.

`reason_recall` is especially misleading: fixture `expected` objects do not include `reason_codes`. The evaluator returns `1.0` when there are zero expected reasons.

### Real-world tests needed

- A consented, de-identified corpus with independent human labels.
- Multiple annotators and disagreement tracking.
- Precision/recall per category, not just aggregate.
- False-positive cost for interruptions.
- Thread-aware tests with quoted history.
- Phishing and spoofed-sender cases.
- Negation and resolved-alert cases.
- Non-English messages.
- HTML-only and malformed MIME.
- Relative dates evaluated against message timestamp/time zone.
- Real scheduling threads over multiple replies.
- Drift tests across personal, work, school, and noisy promotional inboxes.

## 9. Security and Privacy Audit

| Severity | Finding |
| --- | --- |
| **High** | No authentication or authorization. All read and mutation endpoints trust any caller who can reach the backend. |
| **High** | Real message bodies, sender identities, recipient identities, and subjects would be stored plaintext in SQLite. |
| **High** | Reproduced cross-account cache deletion bug removes another account’s thread metadata. |
| **High** | No tenant isolation; `user_id` is hardcoded to `user_001`. |
| **Medium** | OAuth state is in-memory and not bound to a user/browser session; no PKCE. |
| **Medium** | Disconnect deletes local tokens but does not revoke the Google grant. |
| **Medium** | Sync exception paths can commit partial pending data rather than roll back. |
| **Medium** | No retention policy, secure deletion, key rotation, or database encryption. |
| **Medium** | No Alembic migrations or schema-version check. |
| **Medium** | OAuth/token/cursor tables lack several foreign-key and uniqueness constraints. |
| **Medium** | API exposes Google connection emails/status without authentication. |
| **Medium** | No rate limiting, provider retry policy, or abuse controls. |
| **Low** | CORS allows all methods/headers for configured localhost origins; acceptable locally, unsuitable as a complete security boundary. |
| **Low** | Backend dependency vulnerabilities are not scanned by an automated tool. |
| **Info** | No likely secrets or private keys were found committed. |
| **Info** | Local DB and `.env` files are ignored and not tracked. |
| **Info** | Google provider clients contain GET calls only; OAuth token exchange/refresh correctly uses POST. |
| **Info** | No Gmail send/modify or Calendar event write endpoint exists. |

There is no Critical finding under the safe default because real connectors are off. If this service were exposed publicly with real connectors enabled, the missing authentication and plaintext private-data storage would become Critical deployment blockers.

## 10. UI and Product Experience Audit

### Screens that exist

- Command center
- Unified inbox
- Risk radar
- Notifications
- Triage queue
- Triage detail
- Connections
- Integrations
- Rules
- Analytics
- Audit log

### Useful screens

The command center, inbox, radar, notification center, and triage detail communicate the demo concept clearly. Score gauges and reason cards make the deterministic decisions understandable.

### Demo-only/fake elements

- Six account cards are synthetic.
- Notification badge is hardcoded to `25`.
- “All systems monitoring” / monitoring language is presentation, not live provider health.
- Demo sync is a simulated status update.
- Rules do not affect scoring.
- Scheduling review does not enter a real queue.
- Analytics accuracy is fixture conformance.

### Misleading elements

- Connections page labels all returned accounts “Connected” regardless of `connection_status`.
- It gives every account a “Sync demo data” button, including potential real accounts.
- Home says the system analyzed messages across “demo accounts” while backend account counts include real accounts.
- Connections copy still describes Gmail as a future OAuth integration even though V1.1 claims it is complete.
- Integrations UI can represent the connector as ready, but live behavior is unproven.

### Non-functional controls

- Inbox “Filters” button.
- Audit-log search input.
- Triage-detail Snooze button.

### Polished aspects

- Strong visual hierarchy.
- Consistent badges and color system.
- Clear disabled Google safety page.
- Good explanation of priority reasons.
- Build is clean and TypeScript strict mode is enabled.

### Missing for real users

- Login/account setup.
- Onboarding.
- Empty states with recovery actions.
- Confirmation prompts for destructive cache deletion.
- Accessible mobile navigation.
- Thread view/context.
- Actual scheduling queue.
- Rule effect preview.
- Provider error details and recovery.
- Pagination.
- Real account switching when several Google accounts exist.

### Can a user understand what to do?

Yes for the scripted demo. No for unscripted real use. Several controls imply behavior they do not perform, and the product does not distinguish clearly enough between simulated operations and working ones.

### Screenshot truth

The screenshots are visually polished but stale:

- Seven screenshots show the older shell and old “Synthetic messages only / 6 accounts connected” copy.
- `integrations-google-disabled.png` shows Calendar-list read-only scope, which current code removed.
- The README presents them as current product evidence.

## 11. Code Quality and Maintainability Audit

### Test coverage quality

Good for deterministic happy paths and connector guardrails. Weak for real integration, multi-account behavior, UI, error recovery, and production invariants.

Passing 73 tests should not be confused with broad coverage; many are small parametrized keyword checks.

### Naming quality

Generally clear. Module and route names are understandable. “AI,” “sync,” “review queue,” and “rules” carry more behavioral meaning than the implementation supports.

### Module boundaries

Good separation of scoring engines, provider clients, token crypto, routers, and serialization.

Weak boundaries:

- Demo seed and real ingestion duplicate substantial logic.
- Manual deletion logic is separate and brittle.
- Global `LATEST` evaluation state and global OAuth state do not scale.

### Duplicate/dead logic

- Seed and real-ingestion assessment/notification creation are duplicated.
- Demo connector registry is unused.
- Deduper is unused.
- User rules are disconnected.
- Generated JSON fixtures duplicate `seed_data.py` as a second source of truth.

### Error handling

Provider exceptions are hidden safely, but too aggressively:

- Responses often return HTTP 200 with `"failed"` or `"blocked"` statuses.
- Successful partial work may be committed on failure.
- No structured retry/recovery.
- Frontend mostly reduces failures to “backend running?” messages.

### Config handling

Safe defaults and `override=False` local `.env` loading are good. Configuration is still global process state and lacks typed validation at startup.

### Schema/migration risk

High for any evolving real deployment. `create_all()` cannot alter existing tables or perform data migrations.

### Ease of extension

Moderate. The service layout is approachable, but extending it safely requires first removing dead abstractions, centralizing ingestion, adding migrations, and defining real tenancy/auth boundaries.

### Can V1.2 be built cleanly on top?

Not cleanly yet. ActionBridge would add write/approval complexity on top of:

- an unproven live connector,
- no auth,
- no real scheduling queue,
- unsafe cache cleanup,
- partial-commit risk,
- and a misleading evaluation layer.

Those should be resolved before adding outbound or scheduling actions.

## 12. Git and Repository Hygiene Audit

| Item | Status |
| --- | --- |
| Current branch | `main` |
| Latest commit | `27e2b3d Harden Google connector safety and reseed isolation` |
| Local remote-tracking ref | `origin/main` at the same full hash |
| Independent remote query | Not completed; environment failed with Windows Schannel credential error |
| Working tree before this report | **Dirty**: `frontend/next-env.d.ts` modified |
| Cause of modification | Next build changes import from `.next/dev/types/routes.d.ts` to `.next/types/routes.d.ts` |
| Untracked files before this report | None |
| Tracked files before this report | 139 |
| WIP branch | Local `feature/actionbridge-v1.2-wip` at `c024a24` |

Ignored local artifacts found:

- `backend/omnisignal.db`
- Python `__pycache__`
- `.pytest_cache`
- `frontend/node_modules`
- `frontend/.next`
- `frontend/tsconfig.tsbuildinfo`

No tracked `.env`, DB, SQLite, `node_modules`, `.next`, or Python bytecode artifacts were found.

Repository hygiene concerns:

- `backend/evaluation_report.md` is generated output committed as source.
- Generated JSON fixtures duplicate Python seed definitions.
- Eight evidence reports are partly redundant; `BUILD_REPORT.md` and `TEST_REPORT.md` are only redirect stubs.
- Screenshots are stale.
- `frontend/next-env.d.ts` is conventionally tracked by Next.js, but this repo’s dev/build configurations make it oscillate and leave the tree dirty.
- No GitHub Actions or other CI workflow is present.

## 13. Final Product Scorecard

| Area | Score | Why |
| --- | ---: | --- |
| Portfolio value | **7/10** | Polished, coherent demo with meaningful safety work and tests; weakened by overclaiming and disconnected features. |
| Howie relevance | **4/10** | Relevant upstream triage concept, but no scheduling execution, conversation management, or reply loop. |
| Production readiness | **2/10** | No auth, tenancy, migrations, encrypted private-data store, jobs, observability, or real provider proof. |
| Real connector readiness | **4/10** | Solid foundation elements, but mock-only, non-incremental, and affected by cache/evaluation/transaction defects. |
| Security posture | **4/10** | Good default-off/read-only/token-encryption controls; unacceptable production auth and private-data gaps. |
| Code quality | **6/10** | Readable modular code and tests, offset by dead abstractions, duplication, global state, and reproduced defects. |
| UI polish | **6/10** | Visually strong desktop demo; fake controls, stale screenshots, hardcoded values, and no mobile navigation. |
| Evaluation credibility | **2/10** | Fixture conformance on 11 repeated templates; vacuous reason recall; no real data. |
| Extensibility | **5/10** | Approachable structure, but foundational auth, migration, ingestion, and state boundaries are missing. |
| Overall project credibility | **5/10** | Credible as a deterministic portfolio prototype; not credible as a deployed AI secretary or proven connector product. |

## 14. Brutal Final Verdict

**What this product is:**
A polished local-first synthetic inbox-priority demo with deterministic keyword scoring, explainable in-app triage, local audit records, and a mock-tested read-only Google connector foundation.

**What this product is not:**
An AI secretary, scheduling assistant, production inbox, multi-user SaaS, real cross-platform monitor, or proven Google integration.

**What it can honestly claim:**
It demonstrates how synthetic messages from several platform shapes can be normalized, scored with explainable rules, routed into local notification/triage views, and guarded behind a disabled-by-default read-only Google connector architecture.

**What it should stop claiming:**
Working cross-platform integrations, active deduplication, functional user policy, a real TrustOps scheduling queue, real-world accuracy, complete auditability, or Howie-like booking capability.

**What is impressive:**
The visual design, clear safety posture, deterministic explainability, token encryption/refresh scaffolding, account-scoped provider IDs, and disciplined local verification.

**What is weak:**
The gap between UI language and behavior, synthetic/circular evaluation, no authentication, unused architectural components, stale evidence, and lack of any real connector success test.

**What would break first in real use:**
Evaluation/Analytics after real ingestion, keyword accuracy on ordinary email, multi-account cache thread integrity, large-inbox performance, and provider edge/error handling.

**What to fix before V1.2:**
Cross-account cache deletion, evaluation filtering, sync transaction rollback, actual rule behavior or honest removal, demo/real account separation in Connections, live Google validation, and a real scheduling-review data model.

**What to build next:**
Do not build outbound scheduling actions yet. First prove one controlled Google account can connect, refresh, sync, disconnect, and delete its cache without corrupting another account or breaking analytics.

**Whether this is worth showing to Howie:**
Yes, but only as a portfolio architecture prototype—not as a competitor, completed feature, or working secretary.

**How to frame it if shown to Howie:**
“I built a local, explainable attention-triage prototype and a disabled-by-default read-only Google connector foundation. The demo is synthetic; live Google behavior and scheduling actions are not yet proven. The interesting design question is how this upstream risk layer could safely feed a scheduling assistant.”

## 15. Next Action Recommendation

### 1. Option B: Live-test Google connector with a controlled test account

Best next move. It converts the largest unknown into evidence and will expose OAuth, scope, MIME, refresh, Calendar, and deletion problems before more architecture is added.

Required boundary: use a dedicated test account with fake/non-sensitive mail and calendar events.

### 2. Option C: Clean product messaging and docs

The repository currently loses credibility through stale screenshots and claims that exceed the code. Correct framing would immediately improve portfolio value without pretending the product is more complete.

### 3. Option D: Add migrations and production hardening

Necessary before real users or private data. This includes auth, tenancy, Alembic, transaction boundaries, encrypted content/retention policy, provider revocation, and CI—not only migrations.

### 4. Option E: Stop and use as portfolio

Reasonable if the goal is a demonstrator rather than a product. Before stopping, at minimum fix the claims and screenshots so reviewers are not invited to discover contradictions.

### 5. Option A: Build V1.2 ActionBridge

Worst immediate choice. It adds scheduling and eventual write-risk on top of an unproven read connector and known data-integrity/evaluation defects. ActionBridge should follow live connector validation and foundation repair, not precede them.

## Bottom Line

OmniSignal is a good-looking, thoughtfully guarded prototype with a real amount of engineering behind it. Its strongest version is the honest one: a deterministic synthetic risk-radar demo plus Google connector scaffolding.

The code does not support describing it as a real AI secretary, a production-ready inbox intelligence system, or a Howie-style scheduling product. The next credible milestone is not more feature surface. It is proving the existing connector with controlled real infrastructure and fixing the defects that appear when synthetic assumptions stop holding.
