from icecream import ic
from lib.processors.message_dataclasses import *
from lib.variables import *
import datetime


class ClientMessageFactory:

    def action_handler(self, action, msg_body):
        """ отправляет в соответствии с action сообщения на сборку """
        if action == 'on_chat':
            return self.create_on_chat_msg(msg_body)

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

    def create_on_chat_msg(self, msg_body):
        """ возвращает сообщение-словарь on_chat """
        data = {
            'action': 'on_chat',
            'time': str(datetime.datetime.now()),
            'message': msg_body,
        }
        return data
