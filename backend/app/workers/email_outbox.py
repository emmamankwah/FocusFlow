import logging
import time
from datetime import datetime, timedelta, timezone

from cryptography.fernet import InvalidToken
from sqlalchemy import or_

from app.core.email import send_verification_email
from app.core.outbox import decrypt_verification_otp
from app.core.security import verify_password
from app.database.session import SessionLocal
from app.models.email_outbox import EmailOutbox
from app.models.pending_users import PendingUser

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 2
LEASE_DURATION = timedelta(minutes=2)
MAX_ATTEMPTS = 5
MAX_RETRY_DELAY_SECONDS = 300


def process_one_email(db_factory=SessionLocal) -> bool:
    now = datetime.now(timezone.utc)
    with db_factory() as db:
        job = (
            db.query(EmailOutbox)
            .filter(
                or_(
                    (EmailOutbox.status == "pending")
                    & (EmailOutbox.next_attempt_at <= now),
                    (EmailOutbox.status == "processing")
                    & (EmailOutbox.locked_until <= now),
                )
            )
            .order_by(EmailOutbox.created_at, EmailOutbox.id)
            .with_for_update(skip_locked=True)
            .first()
        )
        if job is None:
            return False

        job.status = "processing"
        job.attempts += 1
        job.locked_until = now + LEASE_DURATION
        job_id = job.id
        recipient = job.recipient
        encrypted_otp = job.encrypted_otp
        attempt = job.attempts
        db.commit()

    with db_factory() as db:
        job = db.query(EmailOutbox).filter(EmailOutbox.id == job_id).first()
        pending_user = (
            db.query(PendingUser)
            .filter(PendingUser.email == recipient)
            .with_for_update()
            .first()
        )
        otp = None
        if encrypted_otp and pending_user:
            try:
                otp = decrypt_verification_otp(encrypted_otp)
            except InvalidToken:
                _mark_failed(db, job_id, "OTP payload could not be decrypted")
                logger.error("Outbox job %s could not decrypt its OTP payload", job_id)
                return True

        expires_at = pending_user.otp_expires_at if pending_user else None
        if expires_at is not None and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if (
            not pending_user
            or not otp
            or not expires_at
            or expires_at <= datetime.now(timezone.utc)
            or not verify_password(otp, pending_user.otp_code)
        ):
            _mark_obsolete(db, job_id)
            return True

        try:
            send_verification_email(recipient, otp)
        except Exception as exc:
            delay = min(2 ** attempt, MAX_RETRY_DELAY_SECONDS)
            job.locked_until = None
            job.last_error = type(exc).__name__
            if attempt >= MAX_ATTEMPTS:
                job.status = "failed"
            else:
                job.status = "pending"
                job.next_attempt_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
            db.commit()
            logger.exception("Outbox email job %s failed (%s)", job_id, type(exc).__name__)
            return True

        job.status = "sent"
        job.encrypted_otp = None
        job.locked_until = None
        job.sent_at = datetime.now(timezone.utc)
        job.last_error = None
        db.commit()
    return True


def _mark_obsolete(db, job_id: int) -> None:
    job = db.query(EmailOutbox).filter(EmailOutbox.id == job_id).first()
    if job:
        job.status = "obsolete"
        job.encrypted_otp = None
        job.locked_until = None
        db.commit()


def _mark_failed(db, job_id: int, reason: str) -> None:
    job = db.query(EmailOutbox).filter(EmailOutbox.id == job_id).first()
    if job:
        job.status = "failed"
        job.encrypted_otp = None
        job.locked_until = None
        job.last_error = reason
        db.commit()


def run_worker() -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting verification email outbox worker")
    while True:
        if not process_one_email():
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_worker()
