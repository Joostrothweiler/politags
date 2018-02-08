"""empty message

Revision ID: a477bd904acd
Revises: aa2af61f119b
Create Date: 2018-02-07 14:02:11.016398

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a477bd904acd'
down_revision = 'aa2af61f119b'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('verifications', 'question_id')
    op.drop_table('questions')


def downgrade():
    op.create_table('questions',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('article_id', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('questionable_type', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('questionable_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name='questions_article_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='questions_pkey')
    )

    op.add_column('verifications', sa.Column('question_id', sa.INTEGER(), autoincrement=False, nullable=True))

