from db.client_db import *
from db.client_history_db import *
from db.base import Base
from lib.variables import ENGINE
from sqlalchemy.orm import sessionmaker

Base.metadata.create_all(ENGINE)
