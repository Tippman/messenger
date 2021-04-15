from icecream import ic

from lib.processors.disconnector import Disconnector
from lib.processors.message_dataclasses import *
from lib.processors.message_handlers import MessageRouter
from lib.variables import *
import logging
import logs.config_server_log


class MessageFactory:
    """ Фабрика датаклассов """

    def __init__(self,
                 action_list=ACTION_LIST,
                 msg_router=MessageRouter(),
                 disconnector=Disconnector()):
        self.action_list = action_list
        self.msg_router = msg_router
        self._disconnector = disconnector
        self.logger = logging.getLogger('server_log')

    def on_msg(self, msg_dict, ip_addr, port):
        """ формирует датаклассы и передает в MessageRouter """
        try:
            action = msg_dict['action']

            if action in self.action_list:

                # actions, отправленные клиентом
                if action == 'authenticate':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    request_datacls = AuthenticateMessage(
                        action=action,
                        time=msg_dict['time'],
                        author=msg_dict['user']['account_name'],
                        account_name=msg_dict['user']['account_name'],
                        password=msg_dict['user']['password'],
                    )
                    self.msg_router.on_msg(datacls=request_datacls, ip_addr=ip_addr, port=port)

                elif action == 'on_chat':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    self.msg_router.on_msg(
                        datacls=OnChatMessage(
                            action=action,
                            time=msg_dict['time'],
                            author=msg_dict['user']['account_name'],
                            message=msg_dict['message']
                        ), ip_addr=ip_addr, port=port)

                elif action == 'p2p':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    self.msg_router.on_msg(
                        datacls=P2PMessage(
                            action=action,
                            time=msg_dict['time'],
                            author=msg_dict['user']['account_name'],
                            to=msg_dict['to'],
                            message=msg_dict['message']
                        ), ip_addr=ip_addr, port=port)

                elif action == 'quit':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    self.msg_router.on_msg(
                        datacls=BaseClientMessage(
                            action=action,
                            time=msg_dict['time'],
                            author=msg_dict['user']['account_name'],
                        ), ip_addr=ip_addr, port=port)

                elif action == 'get_contacts':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    request_dataclass = BaseClientMessage(action=action,
                                                          time=msg_dict['time'],
                                                          author=msg_dict['user_login'])
                    self.msg_router.on_msg(datacls=request_dataclass, ip_addr=ip_addr, port=port)

                elif action == 'add_contact' or action == 'del_contact':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    request_dataclass = AddOrRemoveContactMessage(action=action,
                                                                  time=msg_dict['time'],
                                                                  author=msg_dict['user_login'],
                                                                  target_login=msg_dict['target_login'])
                    self.msg_router.on_msg(datacls=request_dataclass, ip_addr=ip_addr, port=port)


                # actions, отправленные cервером
                elif action == 'probe':
                    pass

                elif action == 'probe':
                    pass

                else:
                    self._disconnector.disconnect(ip_addr, port)

        except KeyError:
            # если поймали ошибку ключа - возможно это ответ сервера -> обрабатывается клиентской стороной
            server_response = msg_dict['response']
            if server_response == 100:
                print('Base info msg')
            elif server_response == 101:
                print('Important info msg')
            elif server_response == 200:
                print('Success')
                print(msg_dict['alert'])
            elif server_response == 201:
                print('Created')
            elif server_response == 202:
                print('accepted')
                print(msg_dict['alert'])

        except Exception as e:
            self._disconnector.disconnect(ip_addr, port, e)
