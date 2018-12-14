"""changing pages

Revision ID: cb1b430bc608
Revises: fe9bc3f6c9fe
Create Date: 2018-12-14 09:54:39.080453

"""

# revision identifiers, used by Alembic.
revision = 'cb1b430bc608'
down_revision = 'fe9bc3f6c9fe'

from alembic import op
import sqlalchemy as sa
import datetime

from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Date

def upgrade():
	op.create_table('pages',
		sa.Column('id', sa.Integer, nullable=False),
		sa.Column('qid', sa.String(length=255), nullable=False),
		sa.Column('content_type', sa.String(length=255), nullable=True),
		sa.Column('content', sa.Text, nullable=True),
		sa.Column('created', sa.DateTime(), nullable=True, default=datetime.datetime.utcnow),
		sa.Column('updated', sa.DateTime(), nullable=True, default=datetime.datetime.utcnow),
		sa.Column('expires', sa.DateTime(), nullable=True, default=datetime.datetime.utcnow),
		sa.Column('lifetime', sa.DateTime(), nullable=True, default=datetime.datetime.utcnow),
		sa.PrimaryKeyConstraint('id')
	) 

def downgrade():
	op.drop_table('pages')

