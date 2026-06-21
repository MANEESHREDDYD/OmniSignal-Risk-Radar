from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..api_utils import parse_json
from ..database import get_db
from ..models import UserRule
from ..services.audit_logger import log_action

router = APIRouter(prefix="/api/rules", tags=["rules"])


class RuleBody(BaseModel):
    rule_name: str
    rule_type: str = "keyword"
    conditions: dict = Field(default_factory=dict)
    action: dict = Field(default_factory=dict)
    is_enabled: bool = True


def serialize(rule: UserRule) -> dict:
    return {"id": rule.id, "rule_name": rule.rule_name, "rule_type": rule.rule_type, "conditions": parse_json(rule.conditions_json, {}), "action": parse_json(rule.action_json, {}), "is_enabled": rule.is_enabled}


@router.get("")
def list_rules(db: Session = Depends(get_db)):
    return [serialize(item) for item in db.scalars(select(UserRule).order_by(UserRule.created_at)).all()]


@router.post("")
def create_rule(body: RuleBody, db: Session = Depends(get_db)):
    rule = UserRule(id=f"rule_{uuid.uuid4().hex[:10]}", rule_name=body.rule_name, rule_type=body.rule_type, conditions_json=json.dumps(body.conditions), action_json=json.dumps(body.action), is_enabled=body.is_enabled)
    db.add(rule)
    log_action(db, "User", "Created notification rule", "rule", rule.id, after=body.model_dump())
    db.commit()
    return serialize(rule)


@router.patch("/{rule_id}")
def update_rule(rule_id: str, body: RuleBody, db: Session = Depends(get_db)):
    rule = db.get(UserRule, rule_id)
    if not rule:
        raise HTTPException(404, "Rule not found")
    before = serialize(rule)
    rule.rule_name = body.rule_name
    rule.rule_type = body.rule_type
    rule.conditions_json = json.dumps(body.conditions)
    rule.action_json = json.dumps(body.action)
    rule.is_enabled = body.is_enabled
    log_action(db, "User", "Updated notification rule", "rule", rule_id, before, body.model_dump())
    db.commit()
    return serialize(rule)


@router.delete("/{rule_id}")
def delete_rule(rule_id: str, db: Session = Depends(get_db)):
    rule = db.get(UserRule, rule_id)
    if not rule:
        raise HTTPException(404, "Rule not found")
    before = serialize(rule)
    db.delete(rule)
    log_action(db, "User", "Deleted notification rule", "rule", rule_id, before=before)
    db.commit()
    return {"deleted": True}
