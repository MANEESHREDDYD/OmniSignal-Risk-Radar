# Backend Test Report

Validation date: June 20, 2026  
Environment: Windows, Python 3.11

## Command

Run from the `backend` directory:

```bash
pytest -q
```

## Result

```text
.................................                                        [100%]
33 passed in 0.87s
```

Status: **PASSED**

## Coverage Areas

The 33 tests cover:

- Gmail, Outlook, SMS, iMessage, and calendar normalization
- Urgent-language and deadline detection
- Security, financial, official, and scheduling risk
- Confirmation, document, meeting, and rescheduling action detection
- P0/P1/P2/P3 priority overrides
- Notification routing
- Message deduplication
- Full 80-message evaluation execution

