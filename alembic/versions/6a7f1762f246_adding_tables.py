"""adding tables

Revision ID: 6a7f1762f246
Revises: 
Create Date: 2024-10-31 12:51:59.979717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a7f1762f246'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=False),
    sa.Column('password', sa.LargeBinary(), nullable=False),
    sa.Column('password_salt', sa.LargeBinary(), nullable=False),
    sa.Column('is_super_admin', sa.Boolean(), nullable=False),
    sa.Column('user_type', sa.Enum('ADMIN', 'USER', name='usertype'), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('time_created', sa.DateTime(), nullable=True),
    sa.Column('time_updated', sa.DateTime(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('chat_pdf_conversions',
    sa.Column('name_internal', sa.String(), nullable=False),
    sa.Column('original_filename', sa.String(), nullable=False),
    sa.Column('pdf_filename', sa.String(), nullable=False),
    sa.Column('status', sa.Enum('PROCESSING', 'COMPLETED', 'FAILED', name='chatpdfstatus'), nullable=False),
    sa.Column('created_by_user_id', sa.Uuid(), nullable=False),
    sa.Column('created_by_user_type', sa.Enum('ADMIN', 'USER', name='usertype'), nullable=False),
    sa.Column('wasabi_key', sa.String(), nullable=False),
    sa.Column('zip_wasabi_key', sa.String(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('time_created', sa.DateTime(), nullable=True),
    sa.Column('time_updated', sa.DateTime(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name_internal')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('chat_pdf_conversions')
    op.drop_table('users')
    # ### end Alembic commands ###