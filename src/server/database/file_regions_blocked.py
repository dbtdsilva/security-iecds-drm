import logging
import json
from sqlalchemy import Column, Integer, String, ForeignKey
from base import Base

log = logging.getLogger('file_regions_blocked')

class FileRegionsBlocked(Base):
    __tablename__ = 'file_regions_blocked'

    id = Column(Integer, primary_key=True, nullable=False)
    fileid = Column(Integer, ForeignKey('file.id'), nullable=False)
    region_code = Column(String, nullable=False)


    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        rv = dict()
        rv['id'] = self.id
        rv['fileid'] = self.fileid
        rv['region_code'] = self.region_code
        return rv

    @classmethod
    def from_dict(cls, data):
        return cls(id=data['id'],
                   fileid=data['fileid'],
                   region_code=data['region_code'])
