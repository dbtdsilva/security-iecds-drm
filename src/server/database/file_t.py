import logging
import json
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from base import Base

log = logging.getLogger('file')

class File(Base):
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True)
    author = Column(String)
    path = Column(String)
    title = Column(String)
    category = Column(String)
    production_date = Column(Date)

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        rv = dict()
        rv['id'] = self.id
        rv['author'] = self.author
        rv['path'] = self.path
        rv['title'] = self.title
        rv['category'] = self.category
        rv['production_date'] = str(self.production_date)
        return rv

    @classmethod
    def from_dict(cls, data):
        return cls(id=data['id'],
                   author=data['author'],
                   path=data['path'],
                   title=data['title'],
                   category=data['category'],
                   production_date=data['production_date'])
