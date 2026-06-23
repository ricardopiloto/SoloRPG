"""Add user auth tables and character ownership.

Revision ID: 0003_user_auth
Revises: 0002_images_enabled
Create Date: 2026-06-21
"""

from typing import Sequence, Union

revision: str = "0003_user_auth"
down_revision: Union[str, None] = "0002_images_enabled"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
