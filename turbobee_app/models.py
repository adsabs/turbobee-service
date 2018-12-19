"""
Database models
"""

import sqlalchemy as sa
from adsmutils import get_date, UTCDateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Pages(Base):
    __tablename__ = 'pages'
    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    qid = sa.Column(sa.String(255), nullable=False)
    content_type = sa.Column(sa.String(255), nullable=True)
    content = sa.Column(sa.Text, nullable=True)
    created = sa.Column(UTCDateTime, default=get_date)
    updated = sa.Column(UTCDateTime, default=get_date)
    expires = sa.Column(UTCDateTime, default=get_date)
    lifetime = sa.Column(UTCDateTime, default=get_date)

    def toJSON(self):
        """Returns value formatted as python dict. Oftentimes
        very useful for simple operations"""
        
        return {
            'id': self.id,
            'qid': self.qid,
            'content_type': self.content_type,
            'content': self.content,
            'created': self.created.isoformat(),
            'updated': self.updated.isoformat(),
            'expires': self.expires.isoformat(),
            'lifetime': self.lifetime.isoformat()
        }


class Records(Base):
    __tablename__ = 'records'
    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    bibcode = sa.Column(sa.String(255), nullable=False)
    bib_data = sa.Column(sa.String(255), nullable=True)

    def toJSON(self):
        """Returns value formatted as python dict. Oftentimes
        very useful for simple operations"""
        
        return {
            'id': self.id,
            'bibcode': self.bibcode,
            'bib_data': self.bib_data
        }
