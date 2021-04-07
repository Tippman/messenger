from lib.processors.disconnector import Disconnector
from lib.processors.message_dataclasses import *
from lib.processors.message_handlers import MessageRouter
from lib.variables import *
import logging
import logs.config_server_log


class MessageFactory:
    def __init__(self,
                 action_list=ACTION_LIST,
                 msg_router=MessageRouter(),
                 disconnector=Disconnector()):
        self.action_list = action_list
        self.msg_router = msg_router
        self._disconnector = disconnector
        self.logger = logging.getLogger('server_log')

    def on_msg(self, msg_dict, ip_addr, port):
        try:
            action = msg_dict['action']

            if action in self.action_list:
                if action == 'authenticate':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    return self.msg_router.on_msg(
                        dataclass=AuthenticateMessage(
                            action=action,
                            time=msg_dict['time'],
                            author=msg_dict['user']['account_name'],
                            account_name=msg_dict['user']['account_name'],
                            password=msg_dict['password']
                        ), ip_addr=ip_addr, port=port)

                elif action == 'on_chat':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    return self.msg_router.on_msg(
                        dataclass=OnChatMessage(
                            action=action,
                            time=msg_dict['time'],
                            author=msg_dict['user']['account_name'],
                            message=msg_dict['message']
                        ), ip_addr=ip_addr, port=port)

                elif action == 'p2p':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    return self.msg_router.on_msg(
                        dataclass=P2PMessage(
                            action=action,
                            time=msg_dict['time'],
                            author=msg_dict['user']['account_name'],
                            to=msg_dict['to'],
                            message=msg_dict['message']
                        ), ip_addr=ip_addr, port=port)

                elif action == 'quit':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    return self.msg_router.on_msg(
                        dataclass=BaseClientMessage(
                            action=action,
                            time=msg_dict['time'],
                            author=msg_dict['user']['account_name'],
                        ), ip_addr=ip_addr, port=port)

                else:
                    self._disconnector.disconnect(ip_addr, port)
        except KeyError:
            # если поймали ошибку ключа - возможно это ответ сервера
            pass
        except Exception as e:
            self._disconnector.disconnect(ip_addr, port, e)
