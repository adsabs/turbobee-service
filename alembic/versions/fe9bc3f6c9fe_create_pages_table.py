"""create pages table

Revision ID: fe9bc3f6c9fe
Revises: 2d6221a53fbe
Create Date: 2018-12-12 17:45:19.489892

"""

# revision identifiers, used by Alembic.
revision = 'fe9bc3f6c9fe'
down_revision = None

from alembic import op
import sqlalchemy as sa
from adsmutils import get_date, UTCDateTime

def upgrade():
	op.create_table('pages',
		sa.Column('id', sa.Integer, nullable=False),
		sa.Column('qid', sa.String(length=1024), nullable=False, unique=True),
		sa.Column('content_type', sa.String(length=255), nullable=True),
		sa.Column('content', sa.Binary, nullable=True),
		sa.Column('created', UTCDateTime, nullable=True, default=get_date),
		sa.Column('updated', UTCDateTime, nullable=True, default=get_date),
		sa.Column('expires', UTCDateTime, nullable=True),
		sa.Column('lifetime', UTCDateTime, nullable=True),
		sa.PrimaryKeyConstraint('id')
	) 

def downgrade():
	op.drop_table('pages')

