from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

import os, sys
sys.path.append(os.path.abspath(os.path.abspath(os.path.dirname(__file__)) + "/.."))
from cipher import Cipher as c

Cipher = c()