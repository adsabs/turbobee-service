"""create records table

Revision ID: 4d4a7c10c57e
Revises: fe9bc3f6c9fe
Create Date: 2018-12-19 12:10:29.676054

"""

# revision identifiers, used by Alembic.
revision = '4d4a7c10c57e'
down_revision = 'fe9bc3f6c9fe'

from alembic import op
import sqlalchemy as sa


def upgrade():
	op.create_table('records',
		sa.Column('id', sa.Integer, nullable=False),
		sa.Column('bibcode', sa.String(length=1024), nullable=False, unique=True),
		sa.Column('bib_data', sa.Binary, nullable=True),
		sa.PrimaryKeyConstraint('id')
	) 


def downgrade():
	op.drop_table('records')
