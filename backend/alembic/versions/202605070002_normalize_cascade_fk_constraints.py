"""normalize and enforce cascade foreign keys with explicit names

Revision ID: 202605070002
Revises: 202605070001
Create Date: 2026-05-07
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision = "202605070002"
down_revision = "202605070001"
branch_labels = None
depends_on = None


FK_SPECS: Sequence[tuple[str, str, str, str, str]] = (
    ("conversations", "whatsapp_instance_id", "whatsapp_instances", "id", "conversations_whatsapp_instance_id_fkey"),
    ("messages", "conversation_id", "conversations", "id", "messages_conversation_id_fkey"),
    ("leads", "conversation_id", "conversations", "id", "leads_conversation_id_fkey"),
    ("handoff_events", "conversation_id", "conversations", "id", "handoff_events_conversation_id_fkey"),
    ("agent_runs", "conversation_id", "conversations", "id", "agent_runs_conversation_id_fkey"),
)


def _recreate_fk(
    table_name: str,
    local_column: str,
    referred_table: str,
    referred_column: str,
    constraint_name: str,
    *,
    ondelete: str | None,
) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    fks = inspector.get_foreign_keys(table_name)

    matching_fks = []
    for fk in fks:
        if (
            fk.get("referred_table") == referred_table
            and fk.get("constrained_columns") == [local_column]
            and fk.get("referred_columns") == [referred_column]
        ):
            matching_fks.append(fk)

    for fk in matching_fks:
        fk_name = fk.get("name")
        if fk_name:
            op.drop_constraint(fk_name, table_name, type_="foreignkey")

    op.create_foreign_key(
        constraint_name,
        table_name,
        referred_table,
        [local_column],
        [referred_column],
        ondelete=ondelete,
    )


def upgrade() -> None:
    for table_name, local_column, referred_table, referred_column, constraint_name in FK_SPECS:
        _recreate_fk(
            table_name,
            local_column,
            referred_table,
            referred_column,
            constraint_name,
            ondelete="CASCADE",
        )


def downgrade() -> None:
    for table_name, local_column, referred_table, referred_column, constraint_name in reversed(FK_SPECS):
        _recreate_fk(
            table_name,
            local_column,
            referred_table,
            referred_column,
            constraint_name,
            ondelete=None,
        )
