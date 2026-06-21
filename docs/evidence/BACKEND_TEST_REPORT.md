# Backend Test Report (V1.1.2)

Date: June 21, 2026
Environment: Windows, Python 3.11

## Full suite

```powershell
cd backend
python -m pytest -q
```

```text
........................................................................ [ 91%]
.......                                                                  [100%]
79 passed in 1.79s
```

Status: **PASSED**

## Focused connector, evaluation, rules, and reseed suite

```powershell
python -m pytest -q app/tests/test_google_oauth_guard.py app/tests/test_real_sync_guard.py app/tests/test_token_crypto.py app/tests/test_oauth_token_service.py app/tests/test_google_gmail_connector_mocked.py app/tests/test_google_calendar_connector_mocked.py app/tests/test_real_cache_deletion.py app/tests/test_seed_isolation.py app/tests/test_evaluation.py app/tests/test_user_rule_engine.py
```

```text
...............................................                          [100%]
47 passed in 1.44s
```

Status: **PASSED**

## Important notes

- Google provider behavior is mock-tested only; no live Google account was used.
- Cache isolation is tested with two Google connections sharing provider-style
  message and thread identifiers.
- Evaluation now ignores unlabeled real-style records and reports labeled and
  ignored counts.
- Enabled sender, keyword, minimum-priority, digest, and VIP rules affect
  assessment in tests.
