"""Initial schema baseline.

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-13

SQLite-dev uses `Base.metadata.create_all` on startup.
Run `alembic upgrade head` on PostgreSQL/Supabase deploys.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Schema is created from SQLAlchemy models via app startup or autogenerate.
    # This revision marks the baseline for postgres migrations.
    if op.get_bind().dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    pass
