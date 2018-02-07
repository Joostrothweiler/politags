"""empty message

Revision ID: aa2af61f119b
Revises: bb0bc279bf4c
Create Date: 2018-02-07 13:43:20.852219

"""
from alembic import op
import sqlalchemy as sa
from app import db


# revision identifiers, used by Alembic.
revision = 'aa2af61f119b'
down_revision = 'bb0bc279bf4c'
branch_labels = None
depends_on = None

def upgrade():
    #fill verifiable type and id with the right values.

    existing_data = db.engine.execute("SELECT id, questionable_type, questionable_id FROM questions")

    for res in existing_data:
        question_id = res[0]
        questionable_type = res[1]
        questionable_id = res[2]

        # update verification, set verifiable_type and verifiable_id to questionable... for verification where verification.question_id = question_id
        db.engine.execute("UPDATE verifications SET verifiable_type = '{}', verifiable_id = {} WHERE question_id = {}".format(questionable_type, questionable_id, question_id))

def downgrade():
    pass
