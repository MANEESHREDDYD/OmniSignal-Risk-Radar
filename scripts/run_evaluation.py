from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.database import SessionLocal  # noqa: E402
from app.seed import seed_database  # noqa: E402
from app.services.evaluation_service import run_evaluation  # noqa: E402


def main() -> int:
    with SessionLocal() as db:
        seed_database(db, force=True)
        result = run_evaluation(db)
    summary = {key: value for key, value in result.items() if key != "details"}
    print(json.dumps(summary, indent=2))
    expected = {
        "total_messages": 80,
        "priority_accuracy": 1.0,
        "action_routing_accuracy": 1.0,
        "p0_precision": 1.0,
        "p0_recall": 1.0,
        "reason_recall": 1.0,
        "scheduling_routing_accuracy": 1.0,
        "newsletter_suppression_accuracy": 1.0,
    }
    if summary != expected:
        print("Evaluation did not match the V1.0 release baseline.", file=sys.stderr)
        return 1
    print("Evaluation baseline: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

