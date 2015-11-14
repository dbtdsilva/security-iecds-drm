import logging
import json
from sqlalchemy import Column, Integer, LargeBinary
from base import Base, Cipher

log = logging.getLogger('player')

class Player(Base):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    hash = Column(LargeBinary(Cipher.PLAYER_HASH_LEN), nullable=False)
    playerkey = Column(LargeBinary(Cipher.BLOCK_SIZE), nullable=False)

    def __repr__(self):
        dic = self.to_dict()
        dic['playerkey'] = '__pkey__'
        dic['hash'] = '__hash__'
        return json.dumps(dic, indent=2)

    def to_dict(self):
        rv = dict()
        rv['id'] = self.id
        rv['hash'] = self.hash
        rv['playerkey'] = self.playerkey
        return rv

    @classmethod
    def from_dict(cls, data):
        return cls(id=data['id'],
                   hash=data['hash'],
                   playerkey=data['playerkey'])
