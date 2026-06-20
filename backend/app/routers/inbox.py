from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..api_utils import message_dict
from ..database import get_db
from ..models import MessageThread, UnifiedMessage

router = APIRouter(prefix="/api/inbox", tags=["inbox"])


@router.get("")
def unified_inbox(db: Session = Depends(get_db)):
    messages = db.scalars(select(UnifiedMessage).order_by(UnifiedMessage.received_at.desc())).all()
    return [message_dict(db, item) for item in messages]


@router.get("/threads")
def list_threads(db: Session = Depends(get_db)):
    threads = db.scalars(select(MessageThread).order_by(MessageThread.last_message_at.desc())).all()
    return [
        {
            "id": thread.id,
            "thread_key": thread.thread_key,
            "canonical_subject": thread.canonical_subject,
            "platform_mix": json.loads(thread.platform_mix_json),
            "participants": json.loads(thread.participant_identifiers_json),
            "message_count": thread.message_count,
            "last_message_at": thread.last_message_at,
        }
        for thread in threads
    ]


@router.get("/threads/{thread_id}")
def get_thread(thread_id: str, db: Session = Depends(get_db)):
    thread = db.get(MessageThread, thread_id)
    if not thread:
        raise HTTPException(404, "Thread not found")
    messages = db.scalars(
        select(UnifiedMessage).where(UnifiedMessage.thread_key == thread.thread_key).order_by(UnifiedMessage.sent_at)
    ).all()
    return {"thread": {"id": thread.id, "subject": thread.canonical_subject}, "messages": [message_dict(db, m) for m in messages]}

