import logging
import json
from sqlalchemy import Column, Integer, String, Date, Time
from base import Base

log = logging.getLogger('file')


class File(Base):
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True)
    author = Column(String, nullable=False)
    path = Column(String, nullable=False)
    title = Column(String, nullable=False)
    category = Column(String)
    production_date = Column(Date)
    max_devices = Column(Integer)
    max_plays = Column(Integer)
    start_time_blocking = Column(Time)
    end_time_blocking = Column(Time)
    # There is also a table 1-N relation (file_regions_blocked), a file may have several regions blocked
    #               a table 1-N relation (file_os_blocked), a file may have several operative systems blocked

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        rv = dict()
        rv['id'] = self.id
        rv['author'] = self.author
        rv['path'] = self.path
        rv['title'] = self.title
        rv['category'] = self.category
        rv['production_date'] = str(self.production_date)
        rv['max_devices'] = self.max_devices
        rv['max_plays'] = self.max_plays
        rv['start_time_blocking'] = str(self.start_time_blocking)
        rv['end_time_blocking'] = str(self.end_time_blocking)
        return rv

    @classmethod
    def from_dict(cls, data):
        return cls(id=data['id'],
                   author=data['author'],
                   path=data['path'],
                   title=data['title'],
                   category=data['category'],
                   production_date=data['production_date'],
                   max_devices=data['max_devices'],
                   max_plays=data['max_plays'],
                   start_time_blocking=data['start_time_blocking'],
                   end_time_blocking=data['end_time_blocking'])
