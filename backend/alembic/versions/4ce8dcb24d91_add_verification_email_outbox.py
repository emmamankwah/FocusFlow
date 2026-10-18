"""Add verification email outbox.

Revision ID: 4ce8dcb24d91
Revises: 6678644d10a6
Create Date: 2026-10-18 14:10:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4ce8dcb24d91"
down_revision: Union[str, Sequence[str], None] = "6678644d10a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    expected_columns = {
        "id",
        "recipient",
        "encrypted_otp",
        "status",
        "attempts",
        "next_attempt_at",
        "locked_until",
        "created_at",
        "sent_at",
        "last_error",
    }

    if not inspector.has_table("email_outbox"):
        op.create_table(
            "email_outbox",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("recipient", sa.String(length=255), nullable=False),
            sa.Column("encrypted_otp", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
            sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
            sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("last_error", sa.String(length=255), nullable=True),
        )
        inspector = sa.inspect(bind)
    else:
        actual_columns = {column["name"] for column in inspector.get_columns("email_outbox")}
        missing_columns = expected_columns - actual_columns
        if missing_columns:
            raise RuntimeError(
                "Existing email_outbox table is missing expected columns: "
                + ", ".join(sorted(missing_columns))
            )

    indexes = {index["name"]: index["column_names"] for index in inspector.get_indexes("email_outbox")}
    index_name = "ix_email_outbox_status_next_attempt"
    if index_name not in indexes:
        op.create_index(
            index_name,
            "email_outbox",
            ["status", "next_attempt_at"],
        )
    elif indexes[index_name] != ["status", "next_attempt_at"]:
        raise RuntimeError(f"Existing {index_name} index has unexpected columns")


def downgrade() -> None:
    op.drop_index("ix_email_outbox_status_next_attempt", table_name="email_outbox")
    op.drop_table("email_outbox")
