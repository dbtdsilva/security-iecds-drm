import sys
import os
import logging
import json
from device import Device
from player import Player
from file_t import File
from user import User
from userfile import UserFile
from sqlalchemy import create_engine, Column, \
    Integer, String, LargeBinary, Date
from base import Base
from sqlalchemy.orm import sessionmaker

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

    def create_file(self, author, title, category, production_date):
        f = File(author=author, title=title, category=category, production_date=production_date)
        self.session.add(f)
        self.session.commit()

    def get_file_list(self):
        return self.session.Query(File).all()

    def create_device(self, devicekey):
        dev = Device(devicekey=devicekey)
        self.session.add(dev)
        self.session.commit()

    def create_player(self, playerkey):
        player = Player(playerkey=playerkey)
        self.session.add(player)
        self.session.commit()

BASE_DIR = os.path.dirname(__file__)
#DATABASE_URI = 'sqlite:///%s' % os.path.join(BASE_DIR, 'storage_main.sqlite3')
DATABASE_URI = 'postgresql://postgres:7yl74Zm4ZpcEsPMilEqUa4vNuRt7jvzm@localhost:5432/security'
storage = Storage(DATABASE_URI)
