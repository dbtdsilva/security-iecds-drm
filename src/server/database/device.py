import logging
import json
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.orm import sessionmaker
from base import Base

log = logging.getLogger('device')

class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True)
    deviceid = Column(LargeBinary(32), nullable=False)
    devicekey = Column(LargeBinary(32), nullable=False)    

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        rv = dict()
        rv['id'] = self.id
        rv['deviceid'] = self.deviceid
        rv['devicekey'] = self.devicekey
        return rv

    @classmethod
    def from_dict(cls, data):
        return cls(id=data['id'],
                   deviceid=data['deviceid'],
                   devicekey=data['devicekey'])
