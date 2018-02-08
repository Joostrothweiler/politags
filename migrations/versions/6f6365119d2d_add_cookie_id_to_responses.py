"""empty message

Revision ID: 6f6365119d2d
Revises: d67521cba296
Create Date: 2018-01-30 14:31:59.476754

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f6365119d2d'
down_revision = 'd67521cba296'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('responses', sa.Column('cookie_id', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('responses', 'cookie_id')
    # ### end Alembic commands ###