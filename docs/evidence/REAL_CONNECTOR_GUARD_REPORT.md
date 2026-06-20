# Real Connector Guard Report (V1.1)

Date: June 20, 2026
Environment: Windows 11, Python 3.11

This report documents the safety guarantees of the V1.1 read-only Google
connector foundation and the evidence that they hold.

## Commands

```bash
cd backend
pytest -q app/tests/test_google_oauth_guard.py app/tests/test_real_sync_guard.py \
         app/tests/test_token_crypto.py app/tests/test_oauth_token_service.py \
         app/tests/test_real_cache_deletion.py
```

Plus the equivalent end-to-end smoke harness (see SMOKE_TEST_REPORT.md).

## Results

| Guarantee | Evidence | Status |
| --- | --- | --- |
| `REAL_CONNECTORS_ENABLED=false` blocks OAuth start | `test_oauth_start_blocked_when_disabled` returns `blocked_disabled`; smoke `/api/auth/google/start` → `blocked_disabled` | PASS |
| `REAL_CONNECTORS_ENABLED=false` blocks real sync | `test_*_sync_blocked_when_disabled` return `blocked_disabled`; a `real_sync_runs` row records the blocked attempt | PASS |
| Missing config blocks even when enabled | `test_oauth_start_blocked_missing_config_when_enabled`, `test_sync_blocked_missing_config_when_enabled` → `blocked_missing_config` | PASS |
| Status endpoint always works | `test_status_endpoint_works_when_disabled`; smoke status check | PASS |
| Synthetic demo mode still works | Backend 61/61 tests pass; evaluation 100%; smoke 80-message / 6-account summary PASS | PASS |
| No token appears in logs or responses | Audit entries store only status/counts; `/status` exposes `has_stored_tokens` boolean only; tests assert no `access_token`/`refresh_token`/`client_secret` in payloads/URLs | PASS |
| Tokens encrypted at rest | `test_oauth_token_service` asserts ciphertext ≠ plaintext and no plaintext in DB; `test_token_crypto` round-trip + missing-key block | PASS |
| Cache deletion does not affect synthetic demo data | `test_real_cache_deletion` deletes only the connection's real records (2 messages), preserves demo account + message, writes an audit log | PASS |
| No outbound actions | Connectors/routers contain no send/modify/delete/RSVP/forward/export/attachment paths; connector tests assert read-only methods only | PASS |

## Audited events

OAuth connect, OAuth start, OAuth callback rejection (bad state), token-exchange
failure, sync (gmail/calendar/full), per-message ingestion, disconnect (with
token-deletion count), cache deletion (with counts), blocked attempts, and sync
failures are all written to the audit log without exposing secrets.

## Conclusion

The guard model holds: real connectors are inert and safe by default, every real
endpoint is protected, tokens are encrypted and never exposed, deletion is scoped
to real data only, and no outbound action is possible. Status: **PASSED**.
