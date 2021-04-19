import json

from icecream import ic
import logging

from sqlalchemy import create_engine

import logs.config_server_log

from lib.processors.message_sender import MessageSender
from sqlalchemy.orm import sessionmaker

from lib.processors.disconnector import Disconnector
from lib.processors.message_dataclasses import *
from lib.variables import ENGINE
from db.base import Base
from db.client_db import Client, ClientStorage, ClientHistoryStorage


class ServerMessageHandler:
    # обработка сообщений от клиента на сервере
    def __init__(self,
                 disconnector=Disconnector(),
                 message_sender=MessageSender()):
        self._disconnector = disconnector
        self._message_sender = message_sender
        self._logger = logging.getLogger('server_log')
        self._Session = sessionmaker(bind=ENGINE)
        self._session = self._Session()
        self._client_storage = ClientStorage(self._session)
        self._client_history_storage = ClientHistoryStorage(self._session)

    def on_chat(self, datacls, ip_addr, port):
        pass

    def get_client_contacts(self, datacls, ip_addr=None, port=None):
        """ делает запрос к БД для получения выборки контактов пользователя по логину.
            Результат выборки уходит в Message Sender """
        if self._client_storage.is_client_exist(datacls.author):
            client_contacts_list = self._client_storage.get_client_contacts(datacls.author)

            response_dataclass = SuccessServerMessage(response=202,
                                                      time=str(datetime.now()),
                                                      alert=json.dumps(client_contacts_list))
            self._message_sender.send(response_dataclass)
            self._session.commit()
        else:
            self._disconnector.disconnect(ip_addr, port, f'user with login "{datacls.author}" does not exists')

    def authenticate_client(self, datacls, ip_addr=None, port=None):
        """ проверяет данные авторизации клиента в БД,
        в случае совпадения инициирует сборку сервера об успешной авторищации """
        if self._client_storage.check_auth_data(datacls.account_name, datacls.password):
            # если найдено совпадение логина и пароля - формируем ответ 200 клиенту и вызываем отправку
            self._logger.info('Success authorize client %s:%s', str(ip_addr), str(port))
            user = self._client_storage.get_client(datacls.account_name)
            self._client_history_storage.add_record(user.id, ip_address=f'{str(ip_addr)}:{str(port)}',
                                                    info=f'Success authorization user: {datacls.account_name}',
                                                    time=datetime.now())
            response_dataclass = SuccessServerMessage(response=200,
                                                      time=str(datetime.now()),
                                                      alert=f'<{ip_addr}:{port} {datacls.account_name}>: Success authorize client!')
            self._session.commit()
        else:
            # если совпадений не найдено - ответ 403 клиенту и вызываем отправку
            self._logger.error('Authorization failed. Client %s:%s', str(ip_addr), str(port))
            response_dataclass = ErrorClientMessage(response=403,
                                                    time=str(datetime.now()),
                                                    error=f'<{ip_addr}:{port}>: Wrong login or password!')
        self._message_sender.send(response_dataclass)

    def register(self, datacls):
        pass

    def unregister(self, datacls):
        pass

    def on_peer(self, datacls):
        pass

    def remove_contact_from_client(self, datacls, ip_addr, port):
        """ удаляет контакт из clients_contacts """
        if self._client_storage.is_client_exist(datacls.target_login):
            current_client = self._client_storage.get_client(datacls.author)
            target_client = self._client_storage.get_client(datacls.target_login)

            if target_client in current_client.contacts.all() and target_client != current_client:
                # если target login есть в списке контактов - удаляем
                if datacls.action == 'del_contact':
                    self._logger.info('Adding a client "%s" to "%s" contact list failed! Contact already exists.',
                                      datacls.target_login, datacls.author)
                    current_client.contacts.remove(target_client)
                    self._logger.info('Success removed a client "%s" to "%s" contact list!',
                                      datacls.target_login, datacls.author)
                    self._client_history_storage.add_record(current_client.id,
                                                            ip_address=':'.join((str(ip_addr), str(port))),
                                                            info=f'Success removed a contact "{datacls.target_login}" '
                                                                 f'from user: {datacls.author}',
                                                            time=datetime.now())

                    response_dataclass = SuccessServerMessage(response=200,
                                                              time=str(datetime.now()),
                                                              alert=f'<{ip_addr}:{port} {datacls.author}>: '
                                                                    f'Success add/remove a client "{datacls.target_login}" '
                                                                    f'to/from contact list of user: {datacls.author}!')
                    self._session.commit()
                else:
                    # логин отсутствует в списке контактов или клиент == цель
                    self._logger.info('Removing a client "%s" to "%s" contact list failed! Contact not exists.',
                                      datacls.target_login, datacls.author)
                    response_dataclass = ErrorServerMessage(response=404,
                                                            time=str(datetime.now()),
                                                            error=f'Removing contact failed. Wrong current or target login')
        else:
            # ни один из переданных логинов не найден в базе:
            self._logger.error('Adding contact failed. Wrong current or target login')
            response_dataclass = ErrorServerMessage(response=404,
                                                    time=str(datetime.now()),
                                                    error=f'Adding contact failed. Wrong current or target login')
        # отправляем ответ
        self._message_sender.send(response_dataclass)

    def add_contact_to_client(self, datacls, ip_addr, port):
        """ довавляет контакт из clients_contacts """
        if self._client_storage.is_client_exist(datacls.target_login):
            current_client = self._client_storage.get_client(datacls.author)
            target_client = self._client_storage.get_client(datacls.target_login)

            if target_client not in current_client.contacts.all() and target_client != current_client:
                # если target login нет в списке контактов - добавляем
                if datacls.action == 'add_contact':
                    current_client.contacts.append(target_client)
                    self._logger.info('Success added a client "%s" to "%s" contact list!',
                                      datacls.target_login, datacls.author)

                    self._client_history_storage.add_record(current_client.id,
                                                            ip_address=f'{str(ip_addr)}:{str(port)}',
                                                            info=f'Success adding a contact "{datacls.target_login}" '
                                                                 f'to user: {datacls.author}',
                                                            time=datetime.now())

                    response_dataclass = SuccessServerMessage(response=201,
                                                              time=str(datetime.now()),
                                                              alert=f'<{ip_addr}:{port} {datacls.author}>: '
                                                                    f'Success add/remove a client "{datacls.target_login}" '
                                                                    f'to/from contact list of user: {datacls.author}!')
                    self._session.commit()
            else:
                # если target login есть в списке контактов или автор == цель
                self._logger.info('Adding a client "%s" to "%s" contact list failed! Contact already exists.',
                                  datacls.target_login, datacls.author)
                response_dataclass = ErrorServerMessage(response=404,
                                                        time=str(datetime.now()),
                                                        error=f'Adding contact failed. Wrong current or target login')
        else:
            # ни один из переданных логинов не найден в базе:
            self._logger.error('Adding contact failed. Wrong current or target login')
            response_dataclass = ErrorServerMessage(response=404,
                                                    time=str(datetime.now()),
                                                    error=f'Adding contact failed. Wrong current or target login')
        # отправляем ответ
        self._message_sender.send(response_dataclass)

    def on_unhandled_msg(self, datacls, ip_addr, port):
        self._disconnector.disconnect(ip_addr, port, f'unhandled server routing for {datacls.__str__()}')


class ClientMessageHandler:
    # обработка сообщений от сервера на склиенте
    def status_200(self, dataclass):
        pass

    def status_400(self, dataclass):
        pass


class MessageRouter:
    """ Роутер сообщений. принимает dataclasses и направляет их в соответствующий обработчик
        ServerHandler или ClientHandler """

    def __init__(self,
                 server_msg_handler=ServerMessageHandler(),
                 client_msg_handler=ClientMessageHandler()):
        self.server_msg_handler = server_msg_handler
        self.client_msg_handler = client_msg_handler
        self._logger = logging.getLogger('server_log')

    def on_msg(self, datacls, ip_addr, port):
        """ отправляет входящий dataclass в обработчик"""
        try:
            # server routing
            if isinstance(datacls, AuthenticateMessage):
                self.server_msg_handler.authenticate_client(datacls, ip_addr, port)

            elif isinstance(datacls, OnChatMessage):
                self.server_msg_handler.on_chat(datacls, ip_addr, port)

            elif isinstance(datacls, P2PMessage):
                self.server_msg_handler.on_peer(datacls)

            elif isinstance(datacls, BaseClientMessage):
                if datacls.action == 'get_contacts':
                    self.server_msg_handler.get_client_contacts(datacls, ip_addr, port)
                elif datacls.action == 'quit':
                    self.server_msg_handler.unregister(datacls)

            elif isinstance(datacls, AddContactMessage):
                self._logger.debug('Routing datacls AddOrRemoveContact')
                self.server_msg_handler.add_contact_to_client(datacls, ip_addr, port)

            elif isinstance(datacls, RemoveContactMessage):
                self._logger.debug('Routing datacls AddOrRemoveContact')
                self.server_msg_handler.remove_contact_from_client(datacls, ip_addr, port)

            else:
                self.server_msg_handler.on_unhandled_msg(datacls)

            # client routing

        except AttributeError as e:
            self._logger.error('Attr error %s', e)
            self.server_msg_handler.on_unhandled_msg(dataclass, ip_addr, port)
