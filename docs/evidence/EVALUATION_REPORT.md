# Evaluation Report (V1.1.2)

Date: June 21, 2026
Dataset: 80 explicitly labeled synthetic fixtures

## Command

```powershell
python scripts/run_evaluation.py
```

## Result

```json
{
  "total_messages": 80,
  "labeled_count": 80,
  "ignored_unlabeled_count": 0,
  "priority_accuracy": 1.0,
  "action_routing_accuracy": 1.0,
  "p0_precision": 1.0,
  "p0_recall": 1.0,
  "reason_recall": 1.0,
  "scheduling_routing_accuracy": 1.0,
  "newsletter_suppression_accuracy": 1.0
}
```

```text
Evaluation baseline: PASSED
```

Status: **PASSED**

## Interpretation

This is synthetic fixture conformance, not real-world accuracy. The evaluator
uses only records containing explicit expected labels. Real-style or otherwise
unlabeled records are ignored and counted in `ignored_unlabeled_count`.

Expected reason codes are now present in the fixtures, so `reason_recall` is no
longer a vacuous metric. A separate regression test adds an unlabeled
real-style message and verifies evaluation still succeeds with that record
reported as ignored.
