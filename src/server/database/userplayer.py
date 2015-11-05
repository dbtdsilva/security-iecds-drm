import logging
import json
from sqlalchemy import create_engine, Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from base import Base

log = logging.getLogger('userplayer')

class UserPlayer(Base):
    __tablename__ = 'userplayer'

    userid = Column(Integer, ForeignKey('user.id'), primary_key=True)
    playerid = Column(Integer, ForeignKey('player.id'), primary_key=True)

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        rv = dict()
        rv['userid'] = self.userid
        rv['playerid'] = self.playerid
        return rv

    @classmethod
    def from_dict(cls, data):
        return cls(userid=data['userid'],
                   playerid=data['playerid'])
