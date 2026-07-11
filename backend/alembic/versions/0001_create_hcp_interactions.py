"""create hcp_interactions table

Revision ID: 0001
Revises:
Create Date: 2026-07-11
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "hcp_interactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("hcp_name", sa.String(255), nullable=True),
        sa.Column("interaction_type", sa.String(100), nullable=True),
        sa.Column("interaction_date", sa.Date(), nullable=True),
        sa.Column("interaction_time", sa.Time(), nullable=True),
        sa.Column("attendees", sa.Text(), nullable=True),
        sa.Column("topics_discussed", sa.Text(), nullable=True),
        sa.Column("materials_shared", postgresql.JSONB(), nullable=True),
        sa.Column("samples_distributed", postgresql.JSONB(), nullable=True),
        sa.Column("sentiment", sa.String(20), nullable=True),
        sa.Column("outcomes", sa.Text(), nullable=True),
        sa.Column("follow_up_actions", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_hcp_interactions_hcp_name", "hcp_interactions", ["hcp_name"])


def downgrade() -> None:
    op.drop_index("ix_hcp_interactions_hcp_name", table_name="hcp_interactions")
    op.drop_table("hcp_interactions")
