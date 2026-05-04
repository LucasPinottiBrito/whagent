"""initial schema

Revision ID: 202605010001
Revises:
Create Date: 2026-05-01
"""

from alembic import op
import sqlalchemy as sa


revision = "202605010001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stores",
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("document", sa.String(length=40), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_stores_slug"), "stores", ["slug"], unique=False)

    op.create_table(
        "users",
        sa.Column("store_id", sa.String(length=36), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_store_id"), "users", ["store_id"], unique=False)

    op.create_table(
        "whatsapp_instances",
        sa.Column("store_id", sa.String(length=36), nullable=False),
        sa.Column("instance_name", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("evolution_instance_id", sa.String(length=120), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_whatsapp_instances_instance_name"),
        "whatsapp_instances",
        ["instance_name"],
        unique=True,
    )
    op.create_index(
        op.f("ix_whatsapp_instances_store_id"),
        "whatsapp_instances",
        ["store_id"],
        unique=False,
    )

    op.create_table(
        "customers",
        sa.Column("store_id", sa.String(length=36), nullable=False),
        sa.Column("phone", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("store_id", "phone", name="uq_customer_store_phone"),
    )
    op.create_index(op.f("ix_customers_phone"), "customers", ["phone"], unique=False)
    op.create_index(op.f("ix_customers_store_id"), "customers", ["store_id"], unique=False)

    op.create_table(
        "salespeople",
        sa.Column("store_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("specialty", sa.String(length=80), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_salespeople_store_id"), "salespeople", ["store_id"], unique=False
    )

    op.create_table(
        "conversations",
        sa.Column("store_id", sa.String(length=36), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("whatsapp_instance_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("ai_enabled", sa.Boolean(), nullable=False),
        sa.Column("assigned_salesperson_id", sa.String(length=36), nullable=True),
        sa.Column("last_intent", sa.String(length=120), nullable=True),
        sa.Column("pending_agent_processing", sa.Boolean(), nullable=False),
        sa.Column("last_customer_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_agent_processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_processing_error", sa.Text(), nullable=True),
        sa.Column("processing_attempts", sa.Integer(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assigned_salesperson_id"], ["salespeople.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.ForeignKeyConstraint(["whatsapp_instance_id"], ["whatsapp_instances.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_conversations_assigned_salesperson_id"),
        "conversations",
        ["assigned_salesperson_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversations_customer_id"),
        "conversations",
        ["customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversations_store_id"), "conversations", ["store_id"], unique=False
    )
    op.create_index(
        op.f("ix_conversations_whatsapp_instance_id"),
        "conversations",
        ["whatsapp_instance_id"],
        unique=False,
    )

    op.create_table(
        "messages",
        sa.Column("conversation_id", sa.String(length=36), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("sender_type", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("evolution_message_id", sa.String(length=160), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_messages_conversation_id"),
        "messages",
        ["conversation_id"],
        unique=False,
    )

    op.create_table(
        "leads",
        sa.Column("store_id", sa.String(length=36), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("conversation_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("intent", sa.String(length=120), nullable=True),
        sa.Column("vehicle_interest", sa.String(length=180), nullable=True),
        sa.Column("budget_min", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("budget_max", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("payment_type", sa.String(length=80), nullable=True),
        sa.Column("trade_in_vehicle", sa.String(length=180), nullable=True),
        sa.Column("interest_summary", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("conversation_id", name="uq_lead_conversation"),
    )
    op.create_index(op.f("ix_leads_conversation_id"), "leads", ["conversation_id"], unique=False)
    op.create_index(op.f("ix_leads_customer_id"), "leads", ["customer_id"], unique=False)
    op.create_index(op.f("ix_leads_store_id"), "leads", ["store_id"], unique=False)

    op.create_table(
        "handoff_events",
        sa.Column("conversation_id", sa.String(length=36), nullable=False),
        sa.Column("salesperson_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"]),
        sa.ForeignKeyConstraint(["salesperson_id"], ["salespeople.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_handoff_events_conversation_id"),
        "handoff_events",
        ["conversation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_handoff_events_salesperson_id"),
        "handoff_events",
        ["salesperson_id"],
        unique=False,
    )

    op.create_table(
        "agent_runs",
        sa.Column("conversation_id", sa.String(length=36), nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("output_text", sa.Text(), nullable=True),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("tools_used", sa.JSON(), nullable=True),
        sa.Column("raw_response", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_agent_runs_conversation_id"),
        "agent_runs",
        ["conversation_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("agent_runs")
    op.drop_table("handoff_events")
    op.drop_table("leads")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("salespeople")
    op.drop_table("customers")
    op.drop_table("whatsapp_instances")
    op.drop_table("users")
    op.drop_table("stores")
