"""add parent id to topics

Revision ID: 1bcf42560189
Revises: a477bd904acd
Create Date: 2018-02-08 08:01:39.857280

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1bcf42560189'
down_revision = 'a477bd904acd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('topics', sa.Column('parent_id', sa.INTEGER(), autoincrement=False, nullable=True))

def downgrade():
    op.drop_column('topics', 'parent_id')
