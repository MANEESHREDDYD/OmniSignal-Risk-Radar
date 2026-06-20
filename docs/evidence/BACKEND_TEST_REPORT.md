# Backend Test Report (V1.1)

Date: June 20, 2026
Environment: Windows 11, Python 3.11

## Command

Run from the `backend` directory:

```bash
pytest -q
```

## Result

```text
.............................................................            [100%]
61 passed in 1.66s
```

Status: **PASSED**

## Notes

- V1.0 baseline of **33 tests still passes**; V1.1 adds **28 new tests** for a
  total of **61**.
- All Google tests use **mocked** API responses via injected clients. No network
  calls are made to Google during tests.
- New test files:
  - `test_google_oauth_guard.py` — status works while disabled; OAuth start is
    blocked when disabled and when config is missing; returns a URL only when
    fully configured (and the client secret never appears in it).
  - `test_token_crypto.py` — encrypt/decrypt round-trip; ciphertext ≠ plaintext;
    missing/malformed key blocks encryption.
  - `test_oauth_token_service.py` — tokens stored encrypted (no plaintext in DB);
    decrypt returns original; disconnect deletes tokens; missing key blocks store.
  - `test_google_gmail_connector_mocked.py` — normalization, read-only methods
    only, empty inbox, malformed message, body truncation.
  - `test_google_calendar_connector_mocked.py` — normalization, read-only methods
    only, empty calendar, all-day events.
  - `test_real_sync_guard.py` — real sync blocked when disabled / missing config;
    runs listing available.
  - `test_real_cache_deletion.py` — deletes real records for one connection only,
    preserves synthetic demo data, writes an audit log.
