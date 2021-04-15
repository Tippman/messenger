from datetime import datetime

from sqlalchemy import Column, Integer, String, select, DateTime, ForeignKey, Table
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, relation, backref

from db.base import Base

#  таблица конатктов пользователей
clients_contacts = Table(
    'clients_contacts', Base.metadata,
    Column('client_id', Integer, ForeignKey('users.id')),
    Column('contact_id', Integer, ForeignKey('users.id')),
)


class Client(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    login = Column(String(20), unique=True)
    password = Column(String(30))

    client_histories = relationship("ClientHistory", back_populates='client')
    contacts = relationship(
        'Client', secondary=clients_contacts,
        primaryjoin=(clients_contacts.c.client_id == id),
        secondaryjoin=(clients_contacts.c.contact_id == id),
        backref=backref('clients_contacts', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return f"<Client(id='{self.id}', login='{self.login}', password='{self.password}')>"


class ClientStorage:
    def __init__(self, session):
        self._session = session

    def get_client_contacts(self, login) -> list:
        """ возвращает список контактов (логинов) пользователя """
        client = self.get_client(login)
        return [contact.login for contact in client.contacts.all()]

    def is_client_exist(self, login) -> bool:
        """ проверяет если клиент в базе. возвращает True/False """
        return True if self.get_client(login) else False

    def delete_client(self, login) -> None:
        """ удаляет клиента из базы """
        pass

    def get_client(self, login) -> object:
        """ возвращает объект пользователя """
        user = select(Client).where(Client.login == login)
        result = self._session.execute(user)
        return result.scalars().first()

    def add_client(self, login, password) -> None:
        """ добавляет клиента в БД или выбрасывет исключение если такой клиент уже есть """
        try:
            self._session.add(Client(login=login, password=password))
        except IntegrityError:
            raise ValueError(f'User with login="{login}" already exists')

    def check_auth_data(self, login, password) -> bool:
        """ проверяет логин и пароль при авторизации. Возвращает True если логин и пароль верные """
        if self.is_client_exist(login):
            client = self.get_client(login)
            if client.login == login and client.password == password:
                return True
        return False


class ClientHistory(Base):
    __tablename__ = 'client_history'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("users.id"))
    ip_address = Column(String(30))
    info = Column(String(25))
    time = Column(DateTime)

    client = relationship('Client', back_populates='client_histories')

    def __repr__(self):
        return f'<ClientHistory> id:{self.id} client_id:{self.client_id} ip_addr:{self.ip_address} time:{self.time}'


class ClientHistoryStorage:
    def __init__(self, session):
        self._session = session

    def add_record(self, client_id, ip_address,
                   time=datetime.now(), info=None):
        self._session.add(ClientHistory(client_id=client_id, ip_address=ip_address, time=time, info=info))


