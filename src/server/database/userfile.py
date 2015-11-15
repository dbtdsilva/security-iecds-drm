import logging
import json
from sqlalchemy import Column, Integer, LargeBinary, DateTime, ForeignKey
from base import Base, Cipher
from Crypto.Cipher import AES

log = logging.getLogger('userfile')

class UserFile(Base):
    __tablename__ = 'userfile'

    userid = Column(Integer, ForeignKey('user.id'), primary_key=True)
    fileid = Column(Integer, ForeignKey('file.id'), primary_key=True)
    filekey = Column(LargeBinary(Cipher.BLOCK_SIZE))
    iv = Column(LargeBinary(AES.block_size))
    boughtdate = Column(DateTime, nullable=False)
    played = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        dic = self.to_dict()
        dic['filekey'] = '__fkey__'
        dic['iv'] = '__iv__'
        return json.dumps(dic, indent=2)

    def to_dict(self):
        rv = dict()
        rv['filekey'] = self.filekey
        rv['iv'] = self.iv
        rv['userid'] = self.userid
        rv['fileid'] = self.fileid
        rv['boughtdate'] = str(self.boughtdate)
        rv['played'] = self.played
        return rv

    @classmethod
    def from_dict(cls, data):
        return cls(filekey=data['filekey'],
                   iv=data['iv'],
                   userid=data['userid'],
                   fileid=data['fileid'],
                   boughtdate=data['boughdata'],
                   played=data['played'])
