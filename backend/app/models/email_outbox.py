from sqlalchemy import Column, DateTime, Index, Integer, String, Text
from sqlalchemy.sql import func

from app.database.session import Base


class EmailOutbox(Base):
    __tablename__ = "email_outbox"
    __table_args__ = (
        Index("ix_email_outbox_status_next_attempt", "status", "next_attempt_at"),
    )

    id = Column(Integer, primary_key=True)
    recipient = Column(String(255), nullable=False)
    encrypted_otp = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending", server_default="pending")
    attempts = Column(Integer, nullable=False, default=0, server_default="0")
    next_attempt_at = Column(DateTime(timezone=True), nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(String(255), nullable=True)
