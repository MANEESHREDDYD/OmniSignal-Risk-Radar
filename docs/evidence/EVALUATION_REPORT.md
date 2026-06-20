# Evaluation Report

Validation date: June 20, 2026  
Dataset: 80 synthetic messages across 11 product categories

## Command

Run from the repository root:

```bash
python scripts/run_evaluation.py
```

## Result

```json
{
  "total_messages": 80,
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

The V1.0 deterministic engine achieved 100% across priority and routing checks on the deliberately structured synthetic release dataset:

- Priority accuracy: 100%
- Action-routing accuracy: 100%
- P0 precision: 100%
- P0 recall: 100%
- Expected-reason recall: 100%
- Scheduling-routing accuracy: 100%
- Newsletter-suppression accuracy: 100%

These figures demonstrate consistency against known fixtures. They are not a claim of 100% accuracy on untested real-world private messages.

## V1.1 Re-validation

Re-run on June 20, 2026 after adding the read-only Google connector foundation.
The synthetic evaluation baseline is **unchanged and still PASSES** (all metrics
1.0 across 80 messages). V1.1 adds no synthetic fixtures and does not alter the
scoring engine; real connectors are disabled by default and excluded from the
evaluation dataset.

