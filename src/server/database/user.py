import logging
import json
from sqlalchemy import Column, Integer, String, LargeBinary
from base import Base, Cipher

log = logging.getLogger('user')

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    userkey = Column(LargeBinary(Cipher.BLOCK_SIZE), nullable=False)
    

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
