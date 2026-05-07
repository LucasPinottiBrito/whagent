"""add cascade deletes for conversations and related rows

Revision ID: 202605070001
Revises: 202605040001
Create Date: 2026-05-07
"""

from alembic import op


revision = "202605070001"
down_revision = "202605040001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("conversations_whatsapp_instance_id_fkey", "conversations", type_="foreignkey")
    op.create_foreign_key(
        "conversations_whatsapp_instance_id_fkey",
        "conversations",
        "whatsapp_instances",
        ["whatsapp_instance_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("messages_conversation_id_fkey", "messages", type_="foreignkey")
    op.create_foreign_key(
        "messages_conversation_id_fkey",
        "messages",
        "conversations",
        ["conversation_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("leads_conversation_id_fkey", "leads", type_="foreignkey")
    op.create_foreign_key(
        "leads_conversation_id_fkey",
        "leads",
        "conversations",
        ["conversation_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("handoff_events_conversation_id_fkey", "handoff_events", type_="foreignkey")
    op.create_foreign_key(
        "handoff_events_conversation_id_fkey",
        "handoff_events",
        "conversations",
        ["conversation_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("agent_runs_conversation_id_fkey", "agent_runs", type_="foreignkey")
    op.create_foreign_key(
        "agent_runs_conversation_id_fkey",
        "agent_runs",
        "conversations",
        ["conversation_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("agent_runs_conversation_id_fkey", "agent_runs", type_="foreignkey")
    op.create_foreign_key(
        "agent_runs_conversation_id_fkey",
        "agent_runs",
        "conversations",
        ["conversation_id"],
        ["id"],
    )

    op.drop_constraint("handoff_events_conversation_id_fkey", "handoff_events", type_="foreignkey")
    op.create_foreign_key(
        "handoff_events_conversation_id_fkey",
        "handoff_events",
        "conversations",
        ["conversation_id"],
        ["id"],
    )

    op.drop_constraint("leads_conversation_id_fkey", "leads", type_="foreignkey")
    op.create_foreign_key(
        "leads_conversation_id_fkey",
        "leads",
        "conversations",
        ["conversation_id"],
        ["id"],
    )

    op.drop_constraint("messages_conversation_id_fkey", "messages", type_="foreignkey")
    op.create_foreign_key(
        "messages_conversation_id_fkey",
        "messages",
        "conversations",
        ["conversation_id"],
        ["id"],
    )

    op.drop_constraint("conversations_whatsapp_instance_id_fkey", "conversations", type_="foreignkey")
    op.create_foreign_key(
        "conversations_whatsapp_instance_id_fkey",
        "conversations",
        "whatsapp_instances",
        ["whatsapp_instance_id"],
        ["id"],
    )
