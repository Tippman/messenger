"""Модуль описания структур таблиц и управления БД."""
from datetime import datetime
from hmac import compare_digest

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Table, select)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import backref, relation, relationship

from db.base import Base

#  таблица контактов пользователей
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
    is_auth = Column(Boolean, unique=False, default=False)

    client_histories = relationship("ClientHistory", back_populates='client')
    contacts = relationship(
        'Client', secondary=clients_contacts,
        primaryjoin=(clients_contacts.c.client_id == id),
        secondaryjoin=(clients_contacts.c.contact_id == id),
        backref=backref('clients_contacts', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return f"<Client(id='{self.id}', login='{self.login}', password='{self.password}')>"


class ClientStorage:
    """Класс управления данными в таблице *users*."""

    def __init__(self, session):
        self._session = session

    def get_all_clients(self):
        """Получить список всех пользователей.

        :return: Список всех пользователей (SQL-объекты).
        """
        return self._session.query(Client).all()

    def get_client_contacts(self, login) -> list:
        """Возвращает список контактов (логинов) пользователя."""
        client = self.get_client(login)
        return [contact.login for contact in client.contacts.all()]

    def is_client_exist(self, login) -> bool:
        """Проверяет есть ли клиент в базе.

        :return: True если клиент есть в базе, иначе False.
        """
        return True if self.get_client(login) else False

    def delete_client(self, login) -> None:
        """Удаляет клиента из базы."""
        pass

    def get_client(self, login):
        """Возвращает объект пользователя."""
        user = select(Client).where(Client.login == login)
        result = self._session.execute(user)
        return result.scalars().first()

    def add_client(self, login: str, hash_password: hex) -> None:
        """Добавляет клиента в БД или выбрасывет исключение если такой клиент уже есть.

        :param login: Логин нового клиента.
        :param hash_password: Hex пароля нового клиента.
        """
        try:
            self._session.add(Client(login=login, password=hash_password))
        except IntegrityError:
            raise ValueError(f'User with login="{login}" already exists')

    def check_auth_data(self, login: str, hash_password: hex) -> bool:
        """Проверяет логин и пароль при авторизации. Возвращает True если логин и пароль верные.

        :param login: Логин клиента.
        :param hash_password: Hex пароля клиента.
        """
        if self.is_client_exist(login):
            client = self.get_client(login)
            if client.login == login and compare_digest(client.password, hash_password):
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
    """Класс управляющий таблицей *client_history*."""

    def __init__(self, session):
        self._session = session

    def gat_all_records(self):
        """Возвращает все записи истории."""
        return self._session.query(ClientHistory).all()

    def add_record(self, client_id, ip_address, time=datetime.now(), info=None):
        """Добавляет запись в таблицу *client_history*."""
        self._session.add(ClientHistory(client_id=client_id, ip_address=ip_address, time=time, info=info))
