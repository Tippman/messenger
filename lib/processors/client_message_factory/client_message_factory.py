from icecream import ic
from lib.processors.message_dataclasses import *
from lib.variables import *
import datetime


class ClientMessageFactory:

    def action_handler(self, action, msg_body):
        """ отправляет в соответствии с action сообщения на сборку """
        if action == 'on_chat':
            return self.create_on_chat_msg(msg_body)
        if action == 'add_contact' or action == 'del_contact':
            author_login, target_login = msg_body.split()
            return self.create_response_add_or_remove_client_contact(action=action,
                                                                     author_login=author_login,
                                                                     target_login=target_login)

    def feed(self, msg: str):
        """ принимает сообщение от пользователя и разбивает его на команду и тело команды.
        Перенаправляет в self.action_handler """
        try:
            action, msg_body = msg.split(" ", maxsplit=1)
            if not action.startswith('#') and action[1:] not in ACTION_LIST:
                return None
            else:
                action = action[1:]
                return self.action_handler(action, msg_body)
        except ValueError:
            return None

    def create_auth_message(self, account_name, password):
        """ возвращает сообщение-словарь авторизации """
        data = {
            'action': 'authenticate',
            'time': str(datetime.datetime.now()),
            'user': {
                'account_name': account_name,
                'password': password
            }
        }
        return data

    def create_response_add_or_remove_client_contact(self, action, author_login, target_login):
        """ возвращает словарь с запросом на добавление или удаление контактов пользователя """
        return {'action': action,
                'time': str(datetime.datetime.now()),
                'user_login': author_login,
                'target_login': target_login}

    def create_response_get_client_contacts(self, account_name):
        """ возвращает словарь с запросом списка контактов пользователя """
        return {'action': 'get_contacts',
                'time': str(datetime.datetime.now()),
                'user_login': account_name}

    def create_on_chat_msg(self, msg_body):
        """ возвращает сообщение-словарь on_chat """
        return {'action': 'on_chat',
                'time': str(datetime.datetime.now()),
                'message': msg_body}
