"""Фабрика для сборки сообщений-запросов, оптравляемых клиентом."""
import datetime

from lib.processors.message_dataclasses import *


class ClientMessageFactory:
    """Класс-фабрика сообщений пользователя."""

    @staticmethod
    def create_auth_message(account_name: str, password: str) -> dict:
        """Создает сообщение-словарь авторизации.

        :param account_name: Логин пользователя.
        :param password: Пароль пользователя (сырой).
        :return: Словарь-запрос для отправки на сервер.
        """
        data = {
            'action': 'authenticate',
            'time': str(datetime.datetime.now()),
            'user': {
                'account_name': account_name,
                'password': password
            }
        }
        return data

    @staticmethod
    def create_request_add_or_remove_client_contact(action: str, author_login: str, target_login: str) -> dict:
        """Создает словарь с запросом на добавление или удаление контактов пользователя.

        :param action: Action (add or remove contact).
        :param author_login: Логин пользователя, инициировавшего запрос.
        :param target_login: Логин пользователя, которого необходимо добавить в список контактов.
        :return: Словарь-запрос для отправки на сервер.
        """
        return {'action': action,
                'time': str(datetime.datetime.now()),
                'user_login': author_login,
                'target_login': target_login}

    @staticmethod
    def create_request_get_client_contacts(account_name: str) -> dict:
        """Создает словарь с запросом списка контактов пользователя.

        :param account_name: Логин пользователя, инициировавшего запрос.
        :return: Словарь-запрос для отправки на сервер.
        """
        return {'action': 'get_contacts',
                'time': str(datetime.datetime.now()),
                'user_login': account_name}

    @staticmethod
    def create_p2p_msg(target: str, msg: str, author: str) -> dict:
        """Создает сообщение-словарь для отправки p2p сообщения.

        :param target: Логин получателя сообщения.
        :param msg: Сообщение пользователю.
        :param author: Логин автора сообщения.
        :return: Словарь-запрос для отправки на сервер.
        """
        return {'action': 'p2p',
                'time': str(datetime.datetime.now()),
                'author': author,
                'target': target,
                'message': msg}

    @staticmethod
    def create_register_msg(login: str, password: str) -> dict:
        """Создает сообщение-словарь регистриции пользователя.

        :param login: Логин пользователя, инициировавшего запрос.
        :param password: Пароль пользователя (сырой).
        :return: Словарь-запрос для отправки на сервер.
        """
        return {'action': 'add_new_client',
                'time': str(datetime.datetime.now()),
                'author': login,
                'password': password}
