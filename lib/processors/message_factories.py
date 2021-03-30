from lib.processors.message_dataclasses import *
from lib.processors.message_handlers import MessageRouter
from lib.variables import *


class MessageFactory:
    def __init__(self,
                 action_list=ACTION_LIST,
                 msg_router=MessageRouter()):
        self.action_list = action_list
        self.msg_router = msg_router

    def on_msg(self, dict, msg_size):
        try:
            action = dict['action']

            if action in self.action_list:
                if action == 'authenticate':
                    print(dict['message'], 'auth')
                    self.msg_router.on_msg(
                        dataclass=AuthenticateMessage(
                            action=action,
                            time=dict['time'],
                            author=dict['author'],
                            msg_size=msg_size,
                            account_name=dict['author'],
                            password=dict['password']
                        ))

                elif action == 'on chat':
                    print(dict['message'], 'chat')
                    self.msg_router.on_msg(
                        dataclass=OnChatMessage(
                            action=action,
                            time=dict['time'],
                            author=dict['author'],
                            msg_size=msg_size,
                            message=dict['message']
                        ))

                elif action == 'p2p':
                    print(dict['to'])
                    print(dict['message'])
                    self.msg_router.on_msg(
                        dataclass=P2PMessage(
                            action=action,
                            time=dict['time'],
                            author=dict['author'],
                            msg_size=msg_size,
                            to=dict['to'],
                            message=dict['message']
                        ))

                elif action == 'quit':
                    print('disconnect')
                    self.msg_router.on_msg(
                        dataclass=BaseClientMessage(
                            action=action,
                            time=dict['time'],
                            author=dict['author'],
                            msg_size=msg_size,
                        ))

                else:
                    print('disconnect')
        except:
            print('disconnect')
