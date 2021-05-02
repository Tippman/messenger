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
        self.client_logger = logging.getLogger('client_log')

    def on_msg(self, msg_dict, ip_addr, port, ui_notifier=None, server_queue=None):
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
                    self.msg_router.on_msg(datacls=request_datacls, ip_addr=ip_addr, port=port,
                                           server_queue=server_queue)

                elif action == 'on_chat':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    self.msg_router.on_msg(
                        datacls=OnChatMessage(
                            action=action,
                            time=msg_dict['time'],
                            author=msg_dict['user']['account_name'],
                            message=msg_dict['message']
                        ), ip_addr=ip_addr, port=port, server_queue=server_queue)

                elif action == 'p2p':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    self.msg_router.on_msg(
                        datacls=P2PMessage(
                            action=action,
                            time=msg_dict['time'],
                            author=msg_dict['author'],
                            target=msg_dict['target'],
                            message=msg_dict['message']
                        ), ip_addr=ip_addr, port=port, server_queue=server_queue)

                elif action == 'quit':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    self.msg_router.on_msg(
                        datacls=BaseClientMessage(
                            action=action,
                            time=msg_dict['time'],
                            author=msg_dict['user']['account_name'],
                        ), ip_addr=ip_addr, port=port, server_queue=server_queue)

                elif action == 'get_contacts':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    request_dataclass = BaseClientMessage(action=action,
                                                          time=msg_dict['time'],
                                                          author=msg_dict['user_login'])
                    self.msg_router.on_msg(datacls=request_dataclass, ip_addr=ip_addr, port=port,
                                           server_queue=server_queue)

                elif action == 'add_contact':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    request_dataclass = AddContactMessage(action=action,
                                                          time=msg_dict['time'],
                                                          author=msg_dict['user_login'],
                                                          target_login=msg_dict['target_login'])
                    self.msg_router.on_msg(datacls=request_dataclass, ip_addr=ip_addr, port=port,
                                           server_queue=server_queue)

                elif action == 'del_contact':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    request_dataclass = RemoveContactMessage(action=action,
                                                             time=msg_dict['time'],
                                                             author=msg_dict['user_login'],
                                                             target_login=msg_dict['target_login'])
                    self.msg_router.on_msg(datacls=request_dataclass, ip_addr=ip_addr, port=port,
                                           server_queue=server_queue)
                elif action == 'add_new_client':
                    self.logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    request_dataclass = RegisterMessage(action=action,
                                                        time=msg_dict['time'],
                                                        author=msg_dict['author'],
                                                        password=msg_dict['password'])
                    self.msg_router.on_msg(datacls=request_dataclass, ip_addr=ip_addr, port=port,
                                           server_queue=server_queue)

                # actions, отправленные cервером
                elif action == 'p2p_receive':
                    self.client_logger.debug('factoring "%s" dataclass for %s:%s', action, str(ip_addr), str(port))
                    self.msg_router.on_msg(
                        datacls=P2PMessageReceive(
                            action=action,
                            time=msg_dict['time'],
                            author=msg_dict['author'],
                            message=msg_dict['message']), ip_addr=ip_addr, port=port, ui_notifier=ui_notifier)

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
                response_dataclass = SuccessServerMessage(response=200,
                                                          time=msg_dict['time'],
                                                          alert=msg_dict['alert'])
                self.msg_router.on_msg(datacls=response_dataclass, ip_addr=ip_addr, port=port, ui_notifier=ui_notifier)
            elif server_response == 201:
                self.logger.debug('Get response 201 from server in routing. Created!')
                response_dataclass = SuccessServerMessage(response=201,
                                                          time=msg_dict['time'],
                                                          alert=msg_dict['alert'])
                self.msg_router.on_msg(datacls=response_dataclass, ip_addr=ip_addr, port=port, ui_notifier=ui_notifier)
            elif server_response == 202:
                print('accepted')
                print(msg_dict['alert'])
            elif server_response == 402:
                print(msg_dict['error'])
                response_dataclass = ErrorServerMessage(response=402, time=msg_dict['time'],
                                                        error='Wrong login or password')
                self.msg_router.on_msg(datacls=response_dataclass, ip_addr=ip_addr, port=port, ui_notifier=ui_notifier)
            elif server_response == 409:
                self.logger.debug('Factoring an error. Already exists.')
                response_dataclass = ErrorServerMessage(response=409,
                                                        time=msg_dict['time'],
                                                        error=msg_dict['error'])
                self.msg_router.on_msg(datacls=response_dataclass, ip_addr=ip_addr, port=port, ui_notifier=ui_notifier)

            elif server_response == 410:
                self.logger.debug('Factoring an error. Target is offline.')
                response_dataclass = ErrorClientMessage(response=410,
                                                        time=msg_dict['time'],
                                                        error=msg_dict['error'])
                self.msg_router.on_msg(datacls=response_dataclass, ip_addr=ip_addr, port=port, ui_notifier=ui_notifier)

        except Exception as e:
            self._disconnector.disconnect(ip_addr, port, e)
