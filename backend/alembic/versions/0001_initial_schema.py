"""Initial schema baseline.

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-13

SQLite uses `Base.metadata.create_all` + `schema_patch` on startup.
Alembic revisions are kept for history; no-op on SQLite-only deploys.
"""

from typing import Sequence, Union

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
