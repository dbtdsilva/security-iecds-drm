import sys
import os
import logging 
import json
import device, player, file_t, user, userfile
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, Date
import base
from sqlalchemy.orm import sessionmaker

log = logging.getLogger('storage')

class Storage(object):
    def __init__(self, DATABASE_URI):
        log.info('DATABASE_URI %s' % DATABASE_URI)
        self.DATABASE_URI = DATABASE_URI
        self.engine = create_engine(DATABASE_URI)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        base.Base.metadata.create_all(self.engine)

BASE_DIR = os.path.dirname(__file__)
#DATABASE_URI = 'sqlite:///%s' % os.path.join(BASE_DIR, 'storage_main.sqlite3')
DATABASE_URI = 'postgresql://postgres:7yl74Zm4ZpcEsPMilEqUa4vNuRt7jvzm@localhost:5432/security'
storage = Storage(DATABASE_URI)