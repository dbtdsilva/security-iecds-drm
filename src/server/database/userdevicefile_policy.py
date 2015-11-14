import logging
import json
from sqlalchemy import Column, Integer, ForeignKey
from base import Base

log = logging.getLogger('userdevicefile_policy')

class UserDeviceFilePolicy(Base):
    __tablename__ = 'userdevicefile_policy'

    userid = Column(Integer, ForeignKey('user.id'), primary_key=True)
    fileid = Column(Integer, ForeignKey('file.id'), primary_key=True)
    deviceid = Column(Integer, ForeignKey('device.id'))

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        rv = dict()
        rv['userid'] = self.userid
        rv['fileid'] = self.deviceid
        rv['deviceid'] = self.deviceid
        return rv

    @classmethod
    def from_dict(cls, data):
        return cls(userid=data['userid'],
                   deviceid=data['fileid'],
                   deviceid=data['deviceid'])
