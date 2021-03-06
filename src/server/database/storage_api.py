import os
import logging

# Base controls the current database
from base import Base, Cipher
# Tables
from device import Device
from player import Player
from file_t import File
from user import User
# Tables originated from relations N,M
from userfile import UserFile
from userdevice import UserDevice
from userplayer import UserPlayer
# Policy tables
from file_os_blocked import FileOSBlocked
from file_regions_blocked import FileRegionsBlocked
from userdevicefile_policy import UserDeviceFilePolicy

# SQLAlchemy dependencies
from sqlalchemy import create_engine, Column, \
    Integer, String, LargeBinary, Date
from sqlalchemy_utils import database_exists, drop_database, create_database
from sqlalchemy.orm import sessionmaker, aliased

import datetime
from geoip import geolite2
import httpagentparser
from encfs import insert_encrypted_file

log = logging.getLogger('storage')
encfs_mpassword = None

class Storage(object):
    def __init__(self, DATABASE_URI):
        log.info('DATABASE_URI %s' % DATABASE_URI)
        self.DATABASE_URI = DATABASE_URI
        self.engine = create_engine(DATABASE_URI)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        Base.metadata.create_all(self.engine)

    def create_new_user(self, username, pem):
        usr = User(username=username, hash=Cipher.generateUserHash(pem), userkey=Cipher.generateUserKey())
        self.session.add(usr)
        self.session.commit()

    def create_file(self, author, title, category, production_date, path):
        if encfs_mpassword == None:
            print "You're not able to create any files"
            return
        f = File(author=author, title=title, category=category, production_date=production_date, path=path)
        self.session.add(f)
        self.session.commit()

        insert_encrypted_file(f, encfs_mpassword)

    def get_file_list(self):
        return self.session.query(File).all()

    def create_device(self, devicekey):
        dev = Device(devicekey=devicekey)
        self.session.add(dev)
        self.session.commit()

    def create_player(self, playerkey, pem, filelist):
        filelist_str = ",".join(filelist)
        player = Player(hash=Cipher.generatePlayerHash(pem), playerkey=playerkey, filelist_integrity=filelist_str)
        self.session.add(player)
        self.session.commit()

    def validate_player(self, hash_key):
        return self.session.query(Player).filter_by(hash=hash_key).all() != []

    def get_player_key(self, hash_key):
        query = self.session.query(Player).filter_by(hash=hash_key).all()
        if len(query) != 1:
            return None
        return query[0].playerkey

    def get_player(self, playerkey):
        query = self.session.query(Player).filter_by(playerkey=playerkey).all()
        if len(query) != 1:
            return None
        return query[0]

    def buy_file(self, userid, fileid):
        uf = UserFile(userid=userid, fileid=fileid, iv=Cipher.generateIV(), boughtdate=datetime.datetime.today().isoformat())
        self.session.add(uf)
        self.session.commit()

    def associate_player_to_user(self, user_id, playerkey):
        query = self.session.query(Player).filter_by(playerkey=playerkey).all()
        if len(query) == 0:
            return None
        player_id = query[0].id
        query = self.session.query(UserPlayer).filter_by(userid=user_id).filter_by(playerid=player_id).all()
        if len(query) == 0:
            up = UserPlayer(userid=user_id, playerid=player_id)
            self.session.add(up)
            self.session.commit()

    def associate_device_to_user(self, user_id, devicekey):
        query = self.session.query(Device).filter_by(devicekey=devicekey).all()
        if len(query) == 0:
            self.create_device(devicekey)
            query = self.session.query(Device).filter_by(devicekey=devicekey).all()
        device_id = query[0].id
        query = self.session.query(UserDevice).filter_by(userid=user_id).filter_by(deviceid=device_id).all()
        if len(query) == 0:
            ud = UserDevice(userid=user_id, deviceid=device_id)
            self.session.add(ud)
            self.session.commit()

    def get_user_file_list(self, userid, include_non_bought = False):
        query = self.session.query(User).filter_by(id=userid).all()
        if len(query) != 1:
            return None
        if include_non_bought:
            q = storage.session.query(UserFile).filter_by(userid=userid).subquery('q')
            lrelations = storage.session.query(File, aliased(UserFile,q)).outerjoin(q, q.c.fileid==File.id).all()
        else:
            lrelations = storage.session.query(File, UserFile).\
                filter(UserFile.userid==query[0].id).\
                join(UserFile, UserFile.fileid==File.id).all()

        flist = []
        for (filet, ufile) in lrelations:
            tmp = filet.to_dict()
            if ufile != None:
                tmp['boughtdate'] = str(ufile.boughtdate)
            flist += [ tmp ]
        return flist

    def get_user_identifier(self, pem):
        query = self.session.query(User).filter_by(hash=Cipher.generateUserHash(pem)).all()
        if len(query) != 1:
            return None
        return query[0].id

    def user_has_title(self, user_id, title_id):
        return len(self.session.query(UserFile).filter_by(userid=user_id).filter_by(fileid=title_id).all()) == 1

    def get_file_key(self, user_id, title_id):
        query = self.session.query(UserFile).filter_by(userid=user_id).filter_by(fileid=title_id).all()
        if len(query) != 1:
            return None
        return query[0].filekey

    def get_file_iv(self, user_id, title_id):
        query = self.session.query(UserFile).filter_by(userid=user_id).filter_by(fileid=title_id).all()
        if len(query) != 1:
            return None
        return query[0].iv

    def exists_device_key(self, devicekey):
        query = self.session.query(Device).filter_by(devicekey=devicekey).all()
        return len(query) != 0

    def exists_player_key(self, playerkey):
        query = self.session.query(Player).filter_by(playerkey=playerkey).all()
        return len(query) != 0

    def get_title_details(self, title_id):
        query = self.session.query(File).filter_by(id=title_id).all()
        if len(query) != 1:
            return None
        return query[0]

    def get_user_detail(self, user_id):
        query = self.session.query(User).filter_by(id=user_id).all()
        if len(query) != 1:
            return None
        return query[0]

    def update_file_key(self, file_key, title_id, user_id):
        query = self.session.query(UserFile).filter_by(userid=user_id).filter_by(fileid=title_id)
        if len(query.all()) != 1:
            return None
        if query.all()[0].filekey != None:
            return query.all()[0].filekey
        query.update({UserFile.filekey: file_key})
        self.session.commit()
        return file_key

    def get_file_query(self, fileid):
        query = self.session.query(File).filter_by(id=fileid)
        if len(query.all()) != 1:
            raise Exception("File doesn't exist")
        return query

    def policy_limit_file_plays(self, fileid, max_plays):
        if max_plays < 0:
            raise Exception("Max plays must be a positive number.")
        query = self.get_file_query(fileid)
        query.update({File.max_plays: max_plays})
        self.session.commit()

    def policy_limit_file_max_devices(self, fileid, maxdevices):
        if maxdevices < 0:
            raise Exception("Max devices must be a positive number.")
        query = self.get_file_query(fileid)
        query.update({File.max_devices: maxdevices})
        self.session.commit()

    def policy_limit_file_timespan(self, fileid, start=None, end=None):
        if start == None and end == None:
            raise Exception("No time limits were provided")
        if start == None:
            start = datetime.time(0, 0, 0)
        if end == None:
            end = datetime.time(23, 59, 59)
        if type(start) != datetime.time or type(end) != datetime.time:
            raise Exception("Arguments types accepted for start and end are None or datetime.time")
        if start > end:
            raise Exception("Start time is bigger than end time")
        query = self.get_file_query(fileid)
        query.update({File.start_time_blocking: start.isoformat(), File.end_time_blocking: end.isoformat()})
        self.session.commit()

    def policy_block_system(self, fileid, system):
        if len(self.session.query(FileOSBlocked).filter_by(fileid=fileid).filter_by(system=system).all()) > 0:
            return
        self.get_file_query(fileid)
        fos = FileOSBlocked(fileid=fileid, system=system)
        self.session.add(fos)
        self.session.commit()

    def policy_block_region(self, fileid, region):
        if len(self.session.query(FileRegionsBlocked).filter_by(fileid=fileid).filter_by(region_code=region).all()) > 0:
            return
        self.get_file_query(fileid)
        fos = FileRegionsBlocked(fileid=fileid, region_code=region)
        self.session.add(fos)
        self.session.commit()

    def policy_has_valid_plays(self, fileid, userid):
        file = self.get_file_query(fileid)[0]

        uf = self.session.query(UserFile).filter_by(fileid=fileid).filter_by(userid=userid)
        if len(uf.all()) != 1:
            raise Exception("User didn't bought this file")
        plays = uf.all()[0].played + 1
        return file.max_plays is None or plays <= file.max_plays

    def policy_is_playable_on_device(self, fileid, userid, devicekey):
        q = self.session.query(Device).filter_by(devicekey=devicekey).all()
        if len(q) != 1:
            raise Exception("Device key doesn't exist.")
        deviceid = q[0].id

        q = self.session.query(UserDeviceFilePolicy).filter_by(fileid=fileid).\
            filter_by(userid=userid).all()
        file = self.get_file_query(fileid)[0]

        if len(self.session.query(UserDeviceFilePolicy).filter_by(fileid=fileid).filter_by(userid=userid).\
                       filter_by(deviceid=deviceid).all()) == 0:
            if file.max_devices is not None and len(q) >= file.max_devices:
                return False
            return True
        return file.max_devices is None or len(q) <= file.max_devices

    def policy_is_valid_time(self, fileid, time):
        file = self.get_file_query(fileid)[0]
        start = file.start_time_blocking
        end = file.end_time_blocking
        if start == None and end == None:
            return True
        if start == None:
            return time >= end
        if end == None:
            return time < start
        return time < start or time >= end

    def policy_is_valid_policy_system(self, fileid, user_agent):
        self.get_file_query(fileid)
        parser = httpagentparser.detect(user_agent)
        if 'os' not in parser or 'name' not in parser['os']:
            return True
        q = self.session.query(FileOSBlocked).filter_by(fileid=fileid).filter_by(system=parser['os']['name']).all()
        return len(q) == 0

    def policy_is_valid_policy_region(self, fileid, remote_addr):
        self.get_file_query(fileid)
        match = geolite2.lookup(remote_addr)
        if match is None:
            return True
        q = self.session.query(FileRegionsBlocked).filter_by(fileid=fileid).filter_by(region_code=match.country).all()
        return len(q) == 0

    def policies_valid_update_values(self, fileid, userid, devicekey):
        # Update number of plays for a file
        uf = self.session.query(UserFile).filter_by(fileid=fileid).filter_by(userid=userid)
        if len(uf.all()) != 1:
            raise Exception("User didn't bought this file")
        plays = uf.all()[0].played + 1
        uf.update({UserFile.played: plays})
        self.session.commit()

        # Update device used for the file
        q = self.session.query(Device).filter_by(devicekey=devicekey).all()
        if len(q) != 1:
            raise Exception("Device key doesn't exist.")
        deviceid = q[0].id
        if len(self.session.query(UserDeviceFilePolicy).filter_by(fileid=fileid).filter_by(userid=userid).\
                       filter_by(deviceid=deviceid).all()) == 0:
            udfp = UserDeviceFilePolicy(fileid=fileid, userid=userid, deviceid=deviceid)
            self.session.add(udfp)
            self.session.commit()

BASE_DIR = os.path.dirname(__file__)
DATABASE_URI = 'postgresql://docker:7yl74Zm4ZpcEsPMilEqUa4vNuRt7jvzm@localhost:5432/security'

if __name__ == "__main__":
    import shutil
    if os.path.exists("../files"):
        shutil.rmtree("../files")
    from Crypto.Hash import SHA256
    encfs_mpassword = SHA256.new("185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969").hexdigest()
    if database_exists(DATABASE_URI):
        drop_database(DATABASE_URI)
    create_database(DATABASE_URI)

storage = Storage(DATABASE_URI)

if __name__ == "__main__":
    storage.create_player('\xb8\x8b\xa6Q)c\xd6\x14/\x9dpxc]\xff\x81L\xd2o&\xc2\xd1\x94l\xbf\xa6\x1d\x8fA\xdee\x9c',
                           open('../certificates/players/Security_P3G1_Player_1.crt', 'r').read(),
                           ["../player/resources/images/icon.bmp",
                            "../player/resources/images/icon.png",
                            "../player/resources/images/logo.bmp",
                            "../player/resources/COPY_Security_P3G1_Player_1.crt",
                            "../player/resources/COPY_Security_P3G1_Player_1_key.pem",
                            "../player/resources/COPY_Security_P3G1_Root.crt",
                            "../player/__init__.py",
                            "../player/mylist.py",
                            "../player/playback.py",
                            "../player/player.py"])
    storage.create_player('_\xb5\x8b\x85\xf12\xa3\x99\xa4YB\xeb0P\xda\xfc%\x1fG\xc3Y?\x8c\x84D\x12~\xaaw\x0f\xb6\xde',
                           open('../certificates/players/Security_P3G1_Player_2.crt', 'r').read(),
                           ["../player/resources/images/icon.bmp",
                            "../player/resources/images/icon.png",
                            "../player/resources/images/logo.bmp",
                            "../player/resources/COPY_Security_P3G1_Player_1.crt",
                            "../player/resources/COPY_Security_P3G1_Player_1_key.pem",
                            "../player/resources/COPY_Security_P3G1_Root.crt",
                            "../player/__init__.py",
                            "../player/mylist.py",
                            "../player/playback.py",
                            "../player/player.py"])
    storage.create_file('John Lennon', 'US Blocked', 'Documentary', '2015-04-07', 'news_interview.wmv')
    storage.create_file('Adamaris Doe', 'Linux Blocked', 'Fantasy', '2015-04-07', 'news_interview.wmv')
    storage.create_file('Richard Damon', 'iOS and Macintosh Blocked', 'Action', '2015-04-07', 'sample.mkv')
    storage.create_file('Robert Patrick', '3 Plays Only', 'Action', '2015-04-07', 'news_interview.wmv')
    storage.create_file('John Smith', '0 Plays Only', 'Sci-fi', '2015-04-07', 'sample.mkv')
    storage.create_file('Aiken Madison', '0 Devices Allowed', 'Horror', '2015-04-07', 'news_interview.wmv')
    storage.create_file('Robert Hit', '1 Device Allowed', 'Romance', '2015-04-07', 'sample.mkv')
    storage.create_file('Arnold Schwarzenegger', 'Blocked from 13:00 till 23:59', 'Comedy', '2015-04-07', 'sample.mkv')
    storage.create_file('Alice Furlong', 'Blocked From 0:00 till 13:00', 'Comedy', '2015-04-07', 'sample.mkv')

    storage.policy_block_region(1, 'US')
    storage.policy_block_system(2, 'Linux') # Linux, Windows, iOS, Macintosh, ChromeOS, PlayStation
    storage.policy_block_system(3, 'iOS')
    storage.policy_block_system(3, 'Macintosh')
    storage.policy_limit_file_plays(4, 3)
    storage.policy_limit_file_plays(5, 0)
    storage.policy_limit_file_max_devices(6, 0)
    storage.policy_limit_file_max_devices(7, 1)
    storage.policy_limit_file_timespan(8, start=datetime.time(13, 0, 0))
    storage.policy_limit_file_timespan(9, start=datetime.time(0, 0, 0), end=datetime.time(13, 0, 0))

    #storage.buy_file(1, 1)
    #storage.buy_file(1, 2)
    #storage.buy_file(1, 3)
    #storage.buy_file(1, 4)
    #storage.buy_file(1, 5)
    #storage.buy_file(1, 6)
    #storage.buy_file(1, 7)
    #storage.buy_file(1, 8)
    #storage.buy_file(1, 9)

    #storage.buy_file(2, 1)
    #storage.buy_file(2, 2)
    #storage.buy_file(2, 3)
    #storage.buy_file(2, 4)
    #storage.buy_file(2, 5)
    #storage.buy_file(2, 6)
    #storage.buy_file(2, 7)
    #storage.buy_file(2, 8)
    #storage.buy_file(2, 9)

    
