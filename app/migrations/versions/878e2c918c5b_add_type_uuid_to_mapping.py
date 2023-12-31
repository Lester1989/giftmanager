"""add type uuid to mapping

Revision ID: 878e2c918c5b
Revises: 426675ce0632
Create Date: 2024-01-01 19:38:54.507326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '878e2c918c5b'
down_revision: Union[str, None] = '426675ce0632'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('gift_idea', 'friend_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('gift_idea', 'id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('user_account', 'id',
               existing_type=sa.UUID(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_account', 'id',
               existing_type=sa.UUID(),
               nullable=True)
    op.alter_column('gift_idea', 'id',
               existing_type=sa.UUID(),
               nullable=True)
    op.alter_column('gift_idea', 'friend_id',
               existing_type=sa.UUID(),
               nullable=True)
    # ### end Alembic commands ###
