"""empty message

Revision ID: 4df404f78b9f
Revises: 41308eb732ce
Create Date: 2018-01-30 14:04:51.059109

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4df404f78b9f'
down_revision = '41308eb732ce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('articles',
    sa.Column('id', sa.String(length=200), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('parties',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), server_default='', nullable=False),
    sa.Column('abbreviation', sa.String(length=20), server_default='', nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('politicians',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('system_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=20), server_default='', nullable=False),
    sa.Column('initials', sa.String(length=20), server_default='', nullable=False),
    sa.Column('first_name', sa.String(length=50), server_default='', nullable=False),
    sa.Column('given_name', sa.String(length=50), server_default='', nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=False),
    sa.Column('suffix', sa.String(length=20), server_default='', nullable=False),
    sa.Column('party', sa.String(length=100), server_default='', nullable=False),
    sa.Column('department', sa.String(length=200), server_default='', nullable=False),
    sa.Column('municipality', sa.String(length=100), server_default='', nullable=False),
    sa.Column('role', sa.String(length=100), server_default='', nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('system_id')
    )
    op.create_table('entities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.String(length=200), nullable=True),
    sa.Column('text', sa.String(length=50), server_default='', nullable=False),
    sa.Column('label', sa.String(length=50), server_default='', nullable=True),
    sa.Column('start_pos', sa.Integer(), nullable=True),
    sa.Column('end_pos', sa.Integer(), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.String(length=200), nullable=True),
    sa.Column('question_string', sa.String(length=200), nullable=True),
    sa.Column('questionable_type', sa.String(length=50), nullable=True),
    sa.Column('questionable_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('entity_linkings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('entity_id', sa.Integer(), nullable=True),
    sa.Column('initial_certainty', sa.Float(), nullable=True),
    sa.Column('updated_certainty', sa.Float(), nullable=True),
    sa.Column('linkable_type', sa.String(length=50), nullable=True),
    sa.Column('linkable_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['entity_id'], ['entities.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('responses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('response', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('responses')
    op.drop_table('entity_linkings')
    op.drop_table('questions')
    op.drop_table('entities')
    op.drop_table('politicians')
    op.drop_table('parties')
    op.drop_table('articles')
    # ### end Alembic commands ###