import sys
import os
import logging
import json

# Base controls the current database
from base import Base
# Tables
from device import Device
from player import Player
from file_t import File
from user import User
# Tables originated from relations N,M
from userfile import UserFile
from userdevice import UserDevice
from userplayer import UserPlayer

# SQLAlchemy dependencies
from sqlalchemy import create_engine, Column, \
    Integer, String, LargeBinary, Date
from sqlalchemy_utils import database_exists, drop_database, create_database
from sqlalchemy.orm import sessionmaker

import time

log = logging.getLogger('storage')

class Storage(object):
    def __init__(self, DATABASE_URI):
        log.info('DATABASE_URI %s' % DATABASE_URI)
        self.DATABASE_URI = DATABASE_URI
        self.engine = create_engine(DATABASE_URI)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        Base.metadata.create_all(self.engine)

    def create_user(self, username, userkey):
        usr = User(username=username, userkey=userkey)
        self.session.add(usr)
        self.session.commit()

    def create_file(self, author, title, category, production_date, path):
        f = File(author=author, title=title, category=category, production_date=production_date, path=path)
        self.session.add(f)
        self.session.commit()

    def get_file_list(self):
        return self.session.query(File).all()

    def create_device(self, devicekey):
        dev = Device(devicekey=devicekey)
        self.session.add(dev)
        self.session.commit()

    def create_player(self, playerkey):
        player = Player(playerkey=playerkey)
        self.session.add(player)
        self.session.commit()

    def buy_file(self, userid, fileid):
        uf = UserFile(userid=userid, fileid=fileid, boughtdate=time.strftime("%x %X"))
        self.session.add(uf)
        self.session.commit()

    def get_user_file_list(self, userid):
        query = self.session.query(User).filter_by(id=userid).all()
        if len(query) != 1:
            return "ERROR"
        return self.session.query(UserFile, File).filter_by(userid=query[0].id).join(File, UserFile.fileid==File.id).all()

BASE_DIR = os.path.dirname(__file__)
#DATABASE_URI = 'sqlite:///%s' % os.path.join(BASE_DIR, 'storage_main.sqlite3')
DATABASE_URI = 'postgresql://postgres:7yl74Zm4ZpcEsPMilEqUa4vNuRt7jvzm@localhost:5432/security'

if __name__ == "__main__":
    if database_exists(DATABASE_URI):
        drop_database(DATABASE_URI)
    create_database(DATABASE_URI)

storage = Storage(DATABASE_URI)

if __name__ == "__main__":
    from Crypto import Random
    storage.create_user('taniaalves', Random.new().read(32))
    storage.create_user('diogosilva', Random.new().read(32))
    storage.create_player('\xb8\x8b\xa6Q)c\xd6\x14/\x9dpxc]\xff\x81L\xd2o&\xc2\xd1\x94l\xbf\xa6\x1d\x8fA\xdee\x9c')
    storage.create_file('John Lennon', 'TW News', 'Documentary', '2015-04-07', 'news_interview.wmv')
    storage.create_file('Adamaris Doe', 'Warcraft', 'Fantasy', '2015-04-07', 'news_interview.wmv')
    storage.create_file('Richard Damon', 'TW News', 'Action', '2015-04-07', 'news_interview.wmv')
    storage.create_file('Joe Doe', 'TW News', 'Action', '2015-04-07', 'news_interview.wmv')
    storage.create_file('John Smith', 'TW News', 'Sci-fi', '2015-04-07', 'news_interview.wmv')
    storage.create_file('Aiken Madison', 'TW News', 'Horror', '2015-04-07', 'news_interview.wmv')
    storage.create_file('Robert Hit', 'TW News', 'Romance', '2015-04-07', 'news_interview.wmv')
    storage.create_file('Alice TRE', 'TW News', 'Comedy', '2015-04-07', 'news_interview.wmv')
    storage.buy_file(1, 1)
    storage.buy_file(1, 2)
    storage.buy_file(1, 4)
    storage.buy_file(1, 6)
    storage.buy_file(2, 2)
    storage.buy_file(2, 3)
    storage.buy_file(2, 7)
    storage.buy_file(2, 6)
    