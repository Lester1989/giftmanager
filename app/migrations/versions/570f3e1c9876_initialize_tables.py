"""initialize tables

Revision ID: 570f3e1c9876
Revises: 
Create Date: 2023-12-22 23:02:36.806399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '570f3e1c9876'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gift_idea',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('friend_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('done', sa.Boolean(), nullable=False),
    sa.Column('done_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_account',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('birthday', sa.DateTime(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('receives_christmas_gift', sa.Boolean(), nullable=False),
    sa.Column('receives_birthday_gift', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_account')
    op.drop_table('gift_idea')
    # ### end Alembic commands ###
