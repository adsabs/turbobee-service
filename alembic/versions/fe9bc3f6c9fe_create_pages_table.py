"""create pages table

Revision ID: fe9bc3f6c9fe
Revises: 2d6221a53fbe
Create Date: 2018-12-12 17:45:19.489892

"""

# revision identifiers, used by Alembic.
revision = 'fe9bc3f6c9fe'
down_revision = '2d6221a53fbe'

from alembic import op
import sqlalchemy as sa
import datetime

from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Date

def upgrade():
	op.create_table('pages',
		sa.Column('qid', sa.String(length=255), nullable=False),
		sa.Column('content_type', sa.String(length=255), nullable=True),
		sa.Column('content', sa.Text, nullable=True),
		sa.Column('created', sa.DateTime(), nullable=True, default=datetime.datetime.utcnow),
		sa.Column('updated', sa.DateTime(), nullable=True, default=datetime.datetime.utcnow),
		sa.Column('expires', sa.DateTime(), nullable=True, default=datetime.datetime.utcnow),
		sa.Column('lifetime', sa.DateTime(), nullable=True, default=datetime.datetime.utcnow),
		sa.PrimaryKeyConstraint('qid')
	) 

def downgrade():
	op.drop_table('pages')

