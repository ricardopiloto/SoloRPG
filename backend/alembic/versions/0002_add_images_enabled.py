"""Add images_enabled to game_sessions.

Revision ID: 0002_images_enabled
Revises: 0001_initial
Create Date: 2026-06-21
"""

from typing import Sequence, Union

revision: str = "0002_images_enabled"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
