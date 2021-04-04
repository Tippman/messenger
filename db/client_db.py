from sqlalchemy import Column, Integer, String, select
from sqlalchemy.exc import IntegrityError

from db.base import Base


class Client(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    login = Column(String(20), unique=True)
    password = Column(String)

    def __repr__(self):
        return f"<Client(id='{self.id}', login='{self.login}', password='{self.password}')>"


class ClientStorage:
    def __init__(self, session):
        self._session = session

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
        """ добавляет клиента в БД или выбрасывет исключение если такой клиент уже есть"""
        try:
            with self._session.begin():
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