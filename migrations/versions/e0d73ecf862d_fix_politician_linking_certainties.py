"""fix politician linking certainties

Revision ID: e0d73ecf862d
Revises: 1bcf42560189
Create Date: 2018-02-08 10:32:49.953290

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from app import db

revision = 'e0d73ecf862d'
down_revision = '1bcf42560189'
branch_labels = None
depends_on = None


def upgrade():
    # Initial certainty = 1.0 means that we are 100% sure, which we are never.
    db.engine.execute("UPDATE entity_linkings SET initial_certainty = 0.95, updated_certainty = 0.95 \
                        WHERE initial_certainty = 1 AND updated_certainty = 1 AND linkable_type = 'Politician'")


def downgrade():
    pass