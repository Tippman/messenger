from sqlalchemy import Column, Integer, String, select, DateTime
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from db.base import Base


class ClientHistory(Base):
    __tablename__ = 'client_history'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer)
    ip_address = Column(String(15))
    info = Column(String(25))
    time = Column(DateTime)


class ClientHistoryStorage:
    def __init__(self, session):
        self._session = session

    def add_record(self, client_id, ip_address,
                   time=datetime.now()):
        with self._session.begin():
            self._session.add(ClientHistory(client_id=client_id, ip_address=ip_address, time=time))
