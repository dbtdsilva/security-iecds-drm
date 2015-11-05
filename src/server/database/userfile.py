import logging
import json
from sqlalchemy import create_engine, Column, Integer, LargeBinary, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from base import Base

log = logging.getLogger('userfile')

class UserFile(Base):
    __tablename__ = 'userfile'

    userid = Column(Integer, ForeignKey('user.id'), primary_key=True)
    fileid = Column(Integer, ForeignKey('file.id'), primary_key=True)
    filekey = Column(LargeBinary(32))
    boughtdate = Column(DateTime, nullable=False)

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        rv = dict()
        rv['filekey'] = self.filekey
        rv['userid'] = self.userid
        rv['fileid'] = self.fileid
        rv['boughtdate'] = str(self.boughtdate)
        return rv

    @classmethod
    def from_dict(cls, data):
        return cls(filekey=data['filekey'],
                   userid=data['userid'],
                   fileid=data['fileid'],
                   boughtdate=data['boughdata'])