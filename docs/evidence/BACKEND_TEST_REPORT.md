# Backend Test Report (V1.1.1)

Date: June 20, 2026
Environment: Windows 11, Python 3.11

## Full suite

```bash
cd backend
pytest -q
```

```text
........................................................................ [100%]
73 passed in 2.29s
```

Status: **PASSED**

## Focused Google and reseed safety suite

```bash
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

Status: **PASSED**

## Notes

- All Google provider responses are mocked; no real Google account or API was
  used.
- New coverage verifies demo reseed isolation, safe defaults, token expiry,
  refresh success/failure, refresh-failure connection status, expiring OAuth
  state, and account-scoped Gmail/Calendar IDs.
- The original 33-test V1.0 baseline remains included.
