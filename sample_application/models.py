"""
Database models
"""

import sqlalchemy as sa
from adsmutils import get_date, UTCDateTime

Base = declarative_base()



class FavoriteColor(Base):
    __tablename__ = 'colors'
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(60), unique=True, nullable=False)
    color = sa.Column(sa.String(60), nullable=True)
    updated = sa.Column(UTCDateTime, default=get_date)

    def toJSON(self):
        """Returns value formatted as python dict. Oftentimes
        very useful for simple operations"""
        
        return {
            'id': self.id,
            'username': self.username,
            'color': self.color,
            'updated': self.updated and self.updated.isoformat() or None
        }