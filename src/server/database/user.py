import logging
import json
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from base import Base

log = logging.getLogger('user')

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    userkey = Column(LargeBinary(32))
    

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        rv = dict()
        rv['id'] = self.id
        rv['username'] = self.username
        rv['userkey'] = self.userkey
        return rv

    @classmethod
    def from_dict(cls, data):
        return cls(id=data['id'],
                   username=data['username'],
                   userkey=data['userkey'])
