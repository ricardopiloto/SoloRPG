"""Add images_enabled to game_sessions.

Revision ID: 0002_images_enabled
Revises: 0001_initial
Create Date: 2026-06-21
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0002_images_enabled"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            "ALTER TABLE game_sessions ADD COLUMN IF NOT EXISTS images_enabled BOOLEAN NOT NULL DEFAULT false"
        )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TABLE game_sessions DROP COLUMN IF EXISTS images_enabled")
