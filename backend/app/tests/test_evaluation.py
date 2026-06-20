from app.database import SessionLocal
from app.seed import seed_database
from app.services.evaluation_service import run_evaluation


def test_evaluation_runs_for_all_demo_messages():
    with SessionLocal() as db:
        seed_database(db, force=True)
        report = run_evaluation(db, write_report=False)
    assert report["total_messages"] == 80
    assert report["priority_accuracy"] >= 0.9
    assert report["scheduling_routing_accuracy"] == 1.0
    assert report["newsletter_suppression_accuracy"] == 1.0
