# Real Connector Guard Report (V1.1.1)

Date: June 20, 2026

## Commands

```bash
cd backend
pytest -q app/tests/test_google_oauth_guard.py \
  app/tests/test_real_sync_guard.py \
  app/tests/test_token_crypto.py \
  app/tests/test_oauth_token_service.py \
  app/tests/test_google_gmail_connector_mocked.py \
  app/tests/test_google_calendar_connector_mocked.py \
  app/tests/test_real_cache_deletion.py \
  app/tests/test_seed_isolation.py
```

```text
40 passed in 1.61s
```

```bash
python scripts/smoke_test.py
```

Status: **PASSED**

## Verified guarantees

| Guarantee | Result |
| --- | --- |
| OAuth start is blocked when `REAL_CONNECTORS_ENABLED=false` | PASS |
| Gmail/Calendar real sync is blocked while disabled | PASS |
| Status and sync-run listing remain safely readable | PASS |
| Safe defaults are demo=true, real=false, approval writes=false | PASS |
| OAuth state rejects missing, unknown, reused, and expired values | PASS |
| OAuth state supports multiple valid in-memory development flows | PASS |
| Token expiry is stored from `expires_in` | PASS |
| Valid access tokens do not refresh unnecessarily | PASS |
| Expired tokens refresh and are re-encrypted | PASS |
| Refresh failure marks connection error and sync failed | PASS |
| Same Gmail/Calendar provider ID does not collide across accounts | PASS |
| Force demo reseed preserves OAuth/token/cursor/sync/real-cache rows | PASS |
| Force demo reseed restores six demo accounts and 80 demo messages | PASS |
| Cache deletion removes only selected real-connection data | PASS |
| Responses and audit payloads contain no token or client-secret value | PASS |
| Gmail send/modify and Calendar write surfaces are absent | PASS |

Google connector tests use mocked responses only. No claim of a live Google
account connection is made.
