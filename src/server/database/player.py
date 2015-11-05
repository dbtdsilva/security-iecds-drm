import logging
import json
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from base import Base

log = logging.getLogger('player')

class Player(Base):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    playerkey = Column(LargeBinary(32), nullable=False)    

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        rv = dict()
        rv['id'] = self.id
        rv['playerkey'] = self.playerkey
        return rv

    @classmethod
    def from_dict(cls, data):
        return cls(id=data['id'],
                   playerkey=data['playerkey'])
