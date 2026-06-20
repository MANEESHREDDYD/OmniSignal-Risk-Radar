# Product Roadmap

## V1.0 - Complete

- Six synthetic connected accounts
- 80-message deterministic fixture set
- Unified inbox and message normalization
- Urgency, risk, action-needed, and priority scoring
- Explainable reason taxonomy
- Notification routing and user actions
- TrustOps scheduling-review handoff
- Rules, analytics, and audit log
- Automated tests and evaluation harness
- Local and Docker run paths

## V1.1

- Real connector adapter interfaces for Gmail and Microsoft Graph, without enabling real OAuth by default
- Local LLM second-opinion adapter, disabled by default
- Review correction feedback loop
- Daily and configurable digest generation
- Notification fatigue controls
- Priority calibration dashboard
- Enterprise admin policy controls

## V1.1 Guardrails

- Real-account support must be opt-in.
- Synthetic demo mode remains the default.
- OAuth tokens must never be stored in source control.
- Deterministic reasons remain visible even when a local model contributes a second opinion.
- User corrections must be reviewable and reversible.
- Outbound messaging requires a separate explicit approval boundary.

## Later Opportunities

- Multi-user SecretaryOps workspaces
- Organization-specific VIP and compliance policies
- Encrypted local message cache
- Calibrated confidence and abstention behavior
- Time-based notification budgets
- Provider health and connector observability
- Human-reviewed suggested replies

