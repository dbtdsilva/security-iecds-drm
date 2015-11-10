import logging
import json
from sqlalchemy import Column, Integer, LargeBinary
from base import Base, Cipher

log = logging.getLogger('device')

class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True)
    devicekey = Column(LargeBinary(Cipher.BLOCK_SIZE), nullable=False)

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        rv = dict()
        rv['id'] = self.id
        rv['devicekey'] = self.devicekey
        return rv

    @classmethod
    def from_dict(cls, data):
        return cls(id=data['id'],
                   devicekey=data['devicekey'])
