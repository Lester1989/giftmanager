"""add interactionlogs, switch to uuids

Revision ID: 426675ce0632
Revises: 76b0ad78f56a
Create Date: 2024-01-01 18:34:26.805481

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '426675ce0632'
down_revision: Union[str, None] = '76b0ad78f56a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('important_event',
    sa.Column('friend_id', sa.Uuid(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='public'
    )
    op.create_table('interaction_log',
    sa.Column('friend_id', sa.Uuid(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('via', sa.Enum('telephone', 'email', 'messenger', 'in_person', name='interactionviatype'), nullable=False),
    sa.Column('talking_points', sa.String(), nullable=True),
    sa.Column('ask_again', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='public'
    )
    op.drop_table('contact')
    op.drop_column('gift_idea', 'friend_id')

    op.drop_column('gift_idea', 'id')
    op.add_column('gift_idea',sa.Column( 'friend_id',sa.Uuid()))
    op.add_column('gift_idea',sa.Column(  'id',sa.Uuid()))
    op.drop_column('user_account', 'id')
    op.add_column('user_account', sa.Column( 'id',sa.Uuid()))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_account', 'id',
               existing_type=sa.Uuid(),
               type_=sa.VARCHAR(),
               existing_nullable=False)
    op.alter_column('gift_idea', 'id',
               existing_type=sa.Uuid(),
               type_=sa.VARCHAR(),
               existing_nullable=False)
    op.alter_column('gift_idea', 'friend_id',
               existing_type=sa.Uuid(),
               type_=sa.VARCHAR(),
               existing_nullable=False)
    op.create_table('contact',
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('friend_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('via_telephone', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('via_email', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('via_messenger', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('in_person', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='contact_pkey')
    )
    op.drop_table('interaction_log', schema='public')
    op.drop_table('important_event', schema='public')
    # ### end Alembic commands ###
