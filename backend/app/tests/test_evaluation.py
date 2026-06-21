import json

from app.models import ConnectedAccount, RawMessage, now_iso
from app.seed import seed_database
from app.services.evaluation_service import run_evaluation


def test_evaluation_runs_for_all_demo_messages(db):
    seed_database(db, force=True)
    report = run_evaluation(db, write_report=False)
    assert report["total_messages"] == 80
    assert report["labeled_count"] == 80
    assert report["ignored_unlabeled_count"] == 0
    assert report["priority_accuracy"] >= 0.9
    assert report["reason_recall"] == 1.0
    assert report["scheduling_routing_accuracy"] == 1.0
    assert report["newsletter_suppression_accuracy"] == 1.0


def test_evaluation_ignores_unlabeled_real_style_message(db):
    seed_database(db, force=True)
    db.add(
        ConnectedAccount(
            id="acct_eval_real",
            user_id="user_001",
            platform="google",
            account_label="Controlled real-style fixture",
            account_identifier="controlled@example.test",
            connection_status="connected",
            is_demo=False,
        )
    )
    db.add(
        RawMessage(
            id="raw_eval_real",
            connected_account_id="acct_eval_real",
            external_message_id="gmail:acct_eval_real:unlabeled",
            platform="gmail",
            raw_payload_json=json.dumps(
                {
                    "id": "gmail_acct_eval_real_unlabeled",
                    "category": "real_gmail",
                    "subject": "Unlabeled provider message",
                }
            ),
            received_at=now_iso(),
        )
    )
    db.commit()
    report = run_evaluation(db, write_report=False)
    assert report["labeled_count"] == 80
    assert report["ignored_unlabeled_count"] == 1
    assert report["priority_accuracy"] == 1.0
