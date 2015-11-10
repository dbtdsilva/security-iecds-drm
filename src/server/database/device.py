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
        dic = self.to_dict()
        dic['devicekey'] = '__dkey__'
        return json.dumps(dic, indent=2)

    def to_dict(self):
        rv = dict()
        rv['id'] = self.id
        rv['devicekey'] = self.devicekey
        return rv

    @classmethod
    def from_dict(cls, data):
        return cls(id=data['id'],
                   devicekey=data['devicekey'])
