from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def now_iso() -> str:
    return datetime.now().astimezone().isoformat()


class ConnectedAccount(Base):
    __tablename__ = "connected_accounts"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    platform: Mapped[str] = mapped_column(Text, nullable=False)
    account_label: Mapped[str] = mapped_column(Text, nullable=False)
    account_identifier: Mapped[str] = mapped_column(Text, nullable=False)
    connection_status: Mapped[str] = mapped_column(Text, nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class RawMessage(Base):
    __tablename__ = "raw_messages"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    connected_account_id: Mapped[str] = mapped_column(ForeignKey("connected_accounts.id"))
    external_message_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    platform: Mapped[str] = mapped_column(Text, nullable=False)
    raw_payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    received_at: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class UnifiedMessage(Base):
    __tablename__ = "unified_messages"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    raw_message_id: Mapped[str] = mapped_column(ForeignKey("raw_messages.id"))
    connected_account_id: Mapped[str] = mapped_column(ForeignKey("connected_accounts.id"))
    platform: Mapped[str] = mapped_column(Text, nullable=False)
    thread_key: Mapped[Optional[str]] = mapped_column(Text)
    sender_name: Mapped[Optional[str]] = mapped_column(Text)
    sender_identifier: Mapped[Optional[str]] = mapped_column(Text)
    recipient_identifiers_json: Mapped[str] = mapped_column(Text, default="[]")
    subject: Mapped[Optional[str]] = mapped_column(Text)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    message_url: Mapped[Optional[str]] = mapped_column(Text)
    sent_at: Mapped[str] = mapped_column(Text, nullable=False)
    received_at: Mapped[str] = mapped_column(Text, nullable=False)
    has_attachments: Mapped[bool] = mapped_column(Boolean, default=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class MessageThread(Base):
    __tablename__ = "message_threads"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    canonical_subject: Mapped[Optional[str]] = mapped_column(Text)
    thread_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    platform_mix_json: Mapped[str] = mapped_column(Text, default="[]")
    participant_identifiers_json: Mapped[str] = mapped_column(Text, default="[]")
    first_message_at: Mapped[str] = mapped_column(Text, nullable=False)
    last_message_at: Mapped[str] = mapped_column(Text, nullable=False)
    message_count: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class MessageEntity(Base):
    __tablename__ = "message_entities"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    message_id: Mapped[str] = mapped_column(ForeignKey("unified_messages.id"))
    entity_type: Mapped[str] = mapped_column(Text, nullable=False)
    entity_value: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_value: Mapped[Optional[str]] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    message_id: Mapped[str] = mapped_column(ForeignKey("unified_messages.id"), unique=True)
    urgency_score: Mapped[int] = mapped_column(Integer)
    risk_score: Mapped[int] = mapped_column(Integer)
    action_score: Mapped[int] = mapped_column(Integer)
    priority_score: Mapped[int] = mapped_column(Integer)
    priority_level: Mapped[str] = mapped_column(Text)
    recommended_action: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class RiskReason(Base):
    __tablename__ = "risk_reasons"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    assessment_id: Mapped[str] = mapped_column(ForeignKey("risk_assessments.id"))
    reason_code: Mapped[str] = mapped_column(Text)
    reason_type: Mapped[str] = mapped_column(Text)
    points: Mapped[int] = mapped_column(Integer)
    explanation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class NotificationEvent(Base):
    __tablename__ = "notification_events"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    message_id: Mapped[str] = mapped_column(ForeignKey("unified_messages.id"))
    assessment_id: Mapped[str] = mapped_column(ForeignKey("risk_assessments.id"))
    notification_type: Mapped[str] = mapped_column(Text)
    priority_level: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default="delivered")
    scheduled_for: Mapped[Optional[str]] = mapped_column(Text)
    delivered_at: Mapped[Optional[str]] = mapped_column(Text)
    dismissed_at: Mapped[Optional[str]] = mapped_column(Text)
    snoozed_until: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class UserActionItem(Base):
    __tablename__ = "user_action_items"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    message_id: Mapped[str] = mapped_column(ForeignKey("unified_messages.id"))
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    due_at: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default="open")
    source_platform: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)
    completed_at: Mapped[Optional[str]] = mapped_column(Text)


class SyncRun(Base):
    __tablename__ = "sync_runs"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    connected_account_id: Mapped[str] = mapped_column(ForeignKey("connected_accounts.id"))
    status: Mapped[str] = mapped_column(Text)
    messages_seen: Mapped[int] = mapped_column(Integer, default=0)
    messages_created: Mapped[int] = mapped_column(Integer, default=0)
    messages_updated: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[str] = mapped_column(Text, default=now_iso)
    completed_at: Mapped[Optional[str]] = mapped_column(Text)
    error_message: Mapped[Optional[str]] = mapped_column(Text)


class UserRule(Base):
    __tablename__ = "user_rules"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[str] = mapped_column(Text, default="user_001")
    rule_name: Mapped[str] = mapped_column(Text)
    rule_type: Mapped[str] = mapped_column(Text)
    conditions_json: Mapped[str] = mapped_column(Text)
    action_json: Mapped[str] = mapped_column(Text)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    actor: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(Text)
    target_type: Mapped[str] = mapped_column(Text)
    target_id: Mapped[str] = mapped_column(Text)
    before_json: Mapped[Optional[str]] = mapped_column(Text)
    after_json: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)
