from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy.orm import Session

from ..models import AuditLog


def log_action(
    db: Session,
    actor: str,
    action: str,
    target_type: str,
    target_id: str,
    before: Any = None,
    after: Any = None,
) -> AuditLog:
    entry = AuditLog(
        id=f"audit_{uuid.uuid4().hex[:12]}",
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=target_id,
        before_json=json.dumps(before) if before is not None else None,
        after_json=json.dumps(after) if after is not None else None,
    )
    db.add(entry)
    return entry
