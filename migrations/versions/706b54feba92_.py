"""empty message

Revision ID: 706b54feba92
Revises: f5afb1ae9933
Create Date: 2017-12-05 11:20:43.667677

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '706b54feba92'
down_revision = 'f5afb1ae9933'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('parties',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), server_default='', nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('politicians',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(length=100), server_default='', nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('politicians')
    op.drop_table('parties')
    # ### end Alembic commands ###
