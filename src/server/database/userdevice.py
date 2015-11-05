import logging
import json
from sqlalchemy import create_engine, Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from base import Base

log = logging.getLogger('userdevice')

class UserDevice(Base):
    __tablename__ = 'userdevice'

    userid = Column(Integer, ForeignKey('user.id'), primary_key=True)
    deviceid = Column(Integer, ForeignKey('device.id'), primary_key=True)

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        rv = dict()
        rv['userid'] = self.userid
        rv['deviceid'] = self.deviceid
        return rv

    @classmethod
    def from_dict(cls, data):
        return cls(userid=data['userid'],
                   deviceid=data['deviceid'])
