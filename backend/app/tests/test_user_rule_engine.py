from app.services.priority_engine import assess_message


def rule(rule_id, conditions, action):
    return {
        "id": rule_id,
        "name": rule_id.replace("_", " "),
        "conditions": conditions,
        "action": action,
    }


def test_sender_contains_can_force_minimum_priority():
    result = assess_message(
        {
            "sender_name": "Ada Lovelace",
            "sender_identifier": "ada@example.test",
            "subject": "Hello",
            "body_text": "Just checking in.",
        },
        user_rules=[
            rule(
                "ada_today",
                {"sender_contains": "ada@"},
                {"minimum_priority": "P1_TODAY"},
            )
        ],
    )
    assert result["priority_level"] == "P1_TODAY"
    assert "user_rule_ada_today" in {item["reason_code"] for item in result["reasons"]}


def test_sender_equals_and_keyword_contains_require_all_conditions():
    configured = rule(
        "exact_keyword",
        {
            "sender_equals": "ada@example.test",
            "keyword_contains": "project atlas",
        },
        {"minimum_priority": "P0_IMMEDIATE"},
    )
    matching = assess_message(
        {
            "sender_name": "Ada",
            "sender_identifier": "ada@example.test",
            "subject": "Project Atlas",
            "body_text": "Status update.",
        },
        user_rules=[configured],
    )
    nonmatching = assess_message(
        {
            "sender_name": "Ada",
            "sender_identifier": "ada@example.test",
            "subject": "Different project",
            "body_text": "Status update.",
        },
        user_rules=[configured],
    )
    assert matching["priority_level"] == "P0_IMMEDIATE"
    assert nonmatching["priority_level"] == "P3_LOW"


def test_suppress_to_digest_caps_normal_message_but_not_security():
    suppress = rule(
        "quiet_project",
        {"keyword_contains": "project atlas"},
        {"suppress_to_digest": True},
    )
    normal = assess_message(
        {
            "subject": "Project Atlas urgent approval",
            "body_text": "Please approve this immediately.",
        },
        user_rules=[suppress],
    )
    security = assess_message(
        {
            "subject": "Project Atlas security alert",
            "body_text": "Unknown device. Secure your account immediately.",
        },
        user_rules=[suppress],
    )
    assert normal["priority_level"] == "P2_DIGEST"
    assert normal["recommended_action"] == "add_to_digest"
    assert security["priority_level"] == "P0_IMMEDIATE"


def test_mark_vip_raises_sender_to_today():
    result = assess_message(
        {
            "sender_name": "Board Member",
            "sender_identifier": "board@example.test",
            "subject": "Checking in",
            "body_text": "How are things?",
        },
        user_rules=[
            rule(
                "board_vip",
                {"sender_contains": "board@"},
                {"mark_vip": True},
            )
        ],
    )
    assert result["priority_level"] == "P1_TODAY"
    assert "vip_sender" in {item["reason_code"] for item in result["reasons"]}
