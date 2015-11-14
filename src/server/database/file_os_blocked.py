import logging
import json
from sqlalchemy import Column, Integer, String, ForeignKey
from base import Base

log = logging.getLogger('file_os_blocked')

class FileOSBlocked(Base):
    __tablename__ = 'file_os_blocked'

    id = Column(Integer, primary_key=True, nullable=False)
    fileid = Column(Integer, ForeignKey('file.id'), nullable=False)
    system = Column(String, nullable=False) # linux*, darwin (this one is OS X), win*, others..

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        rv = dict()
        rv['id'] = self.id
        rv['fileid'] = self.fileid
        rv['system'] = self.system
        return rv

    @classmethod
    def from_dict(cls, data):
        return cls(id=data['id'],
                   fileid=data['fileid'],
                   system=data['system'])
