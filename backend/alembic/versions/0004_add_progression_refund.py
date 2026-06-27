"""Add progression refund window fields to player_characters.

Revision ID: 0004_progression_refund
Revises: 0003_user_auth
Create Date: 2026-06-26
"""

from typing import Sequence, Union

revision: str = "0004_progression_refund"
down_revision: Union[str, None] = "0003_user_auth"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
