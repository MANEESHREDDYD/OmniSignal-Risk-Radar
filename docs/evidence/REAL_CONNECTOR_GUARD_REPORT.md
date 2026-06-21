# Real Connector Guard Report (V1.1.2)

Date: June 21, 2026

## Commands and results

```powershell
cd backend
python -m pytest -q app/tests/test_google_oauth_guard.py app/tests/test_real_sync_guard.py app/tests/test_token_crypto.py app/tests/test_oauth_token_service.py app/tests/test_google_gmail_connector_mocked.py app/tests/test_google_calendar_connector_mocked.py app/tests/test_real_cache_deletion.py app/tests/test_seed_isolation.py app/tests/test_evaluation.py app/tests/test_user_rule_engine.py
```

```text
47 passed in 1.44s
```

```powershell
python scripts/smoke_test.py
```

Status: **PASSED**

## Verified guarantees

| Guarantee | Result |
| --- | --- |
| OAuth start is blocked when `REAL_CONNECTORS_ENABLED=false` | PASS |
| Real sync is blocked while disabled | PASS |
| Synthetic demo mode still works with six accounts and 80 messages | PASS |
| OAuth state is expiring, single-use, and rejects unknown values | PASS |
| Tokens are encrypted and refreshed before expiry when mocked | PASS |
| Same Gmail/Calendar provider ID is account-scoped | PASS |
| Demo reseed preserves real connector state | PASS |
| Deleting account A cache preserves account B messages and threads | PASS |
| Cache deletion audit includes deletion counts | PASS |
| Connector responses contain no token or client-secret fields | PASS |
| Gmail send/modify and Calendar write surfaces are absent | PASS |

Google behavior is mock-tested only. No live Gmail or Google Calendar
connection is claimed.
