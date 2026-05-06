"""initial whagent schema

Revision ID: 202605040001
Revises:
Create Date: 2026-05-04
"""

from alembic import op
import sqlalchemy as sa


revision = "202605040001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stores",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False),
        sa.Column("document", sa.String(40)),
        sa.Column("phone", sa.String(40)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_stores_slug", "stores", ["slug"])

    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id")),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(160), nullable=False),
        sa.Column("role", sa.String(30), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_store_id", "users", ["store_id"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "whatsapp_instances",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id"), nullable=False),
        sa.Column("instance_name", sa.String(120), nullable=False),
        sa.Column("phone", sa.String(40)),
        sa.Column("evolution_instance_id", sa.String(120)),
        sa.Column("webhook_secret", sa.String(160), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("instance_name"),
    )
    op.create_index("ix_whatsapp_instances_store_id", "whatsapp_instances", ["store_id"])
    op.create_index(
        "ix_whatsapp_instances_instance_name", "whatsapp_instances", ["instance_name"]
    )

    op.create_table(
        "customers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id"), nullable=False),
        sa.Column("phone", sa.String(40), nullable=False),
        sa.Column("name", sa.String(160)),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("store_id", "phone", name="uq_customer_store_phone"),
    )
    op.create_index("ix_customers_store_id", "customers", ["store_id"])
    op.create_index("ix_customers_phone", "customers", ["phone"])

    op.create_table(
        "conversations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id"), nullable=False),
        sa.Column("customer_id", sa.String(36), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column(
            "whatsapp_instance_id",
            sa.String(36),
            sa.ForeignKey("whatsapp_instances.id"),
            nullable=False,
        ),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("ai_enabled", sa.Boolean(), nullable=False),
        sa.Column("assigned_salesperson_id", sa.String(36), sa.ForeignKey("users.id")),
        sa.Column("last_intent", sa.String(120)),
        sa.Column("pending_agent_processing", sa.Boolean(), nullable=False),
        sa.Column("last_customer_message_at", sa.DateTime(timezone=True)),
        sa.Column("last_agent_processed_at", sa.DateTime(timezone=True)),
        sa.Column("last_agent_processed_message_id", sa.String(36)),
        sa.Column("last_processing_error", sa.Text()),
        sa.Column("processing_attempts", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_conversations_store_id", "conversations", ["store_id"])
    op.create_index("ix_conversations_customer_id", "conversations", ["customer_id"])
    op.create_index(
        "ix_conversations_whatsapp_instance_id",
        "conversations",
        ["whatsapp_instance_id"],
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(36),
            sa.ForeignKey("conversations.id"),
            nullable=False,
        ),
        sa.Column("direction", sa.String(20), nullable=False),
        sa.Column("sender_type", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("evolution_message_id", sa.String(160)),
        sa.Column("raw_payload", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])
    op.create_index(
        "uq_messages_evolution_message_id_not_null",
        "messages",
        ["evolution_message_id"],
        unique=True,
        postgresql_where=sa.text("evolution_message_id IS NOT NULL"),
    )

    op.create_table(
        "leads",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id"), nullable=False),
        sa.Column("customer_id", sa.String(36), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column(
            "conversation_id",
            sa.String(36),
            sa.ForeignKey("conversations.id"),
            nullable=False,
        ),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("intent", sa.String(120)),
        sa.Column("vehicle_interest", sa.String(180)),
        sa.Column("budget_min", sa.Numeric(12, 2)),
        sa.Column("budget_max", sa.Numeric(12, 2)),
        sa.Column("payment_type", sa.String(80)),
        sa.Column("trade_in_vehicle", sa.String(180)),
        sa.Column("interest_summary", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("conversation_id", name="uq_lead_conversation"),
    )

    op.create_table(
        "handoff_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(36),
            sa.ForeignKey("conversations.id"),
            nullable=False,
        ),
        sa.Column("salesperson_id", sa.String(36), sa.ForeignKey("users.id")),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("reason", sa.Text()),
        sa.Column("metadata", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "agent_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(36),
            sa.ForeignKey("conversations.id"),
            nullable=False,
        ),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("output_text", sa.Text()),
        sa.Column("model", sa.String(120)),
        sa.Column("tools_used", sa.JSON()),
        sa.Column("raw_response", sa.JSON()),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("error", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("agent_runs")
    op.drop_table("handoff_events")
    op.drop_table("leads")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("customers")
    op.drop_table("whatsapp_instances")
    op.drop_table("users")
    op.drop_table("stores")
