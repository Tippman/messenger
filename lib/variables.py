""" Константы используемые в файлах проекта"""
import logging
import ipaddress
from sqlalchemy import create_engine

# server connection vars
DEFAULT_PORT = 7777  # порт по умолчанию
DEFAULT_IP = '127.0.0.1'  # IP адрес по умолчанию
SERVER_ADDR = (DEFAULT_IP, DEFAULT_PORT)  # адрес по умолчанию
MAX_CONNECTIONS = 5  # максимальная очередь подключений

# encoding vars
ENCODING_FORMAT = 'utf-8'  # кодировка

# messages vars
MAX_MSG_SIZE = 1024  # max длина сообщения в байтах

# pack headers vars
HEADER_MSG_LENGTH_BYTES = 'h'  # длина заголовка сообщения - 2 байта
HEADER_IP_BYTES = '4s'  # длина заголовка IP адрес клиента - 4 байта
HEADER_PORT_BYTES = 'h'  # длина заголовка PORT - 2 байта
PACK_FORMAT = f'{HEADER_MSG_LENGTH_BYTES}{HEADER_IP_BYTES}{HEADER_PORT_BYTES}{MAX_MSG_SIZE - 8}s'

# database settings
ENGINE = create_engine('sqlite:///../messenger.sqlite3', echo=True)

# ACTIONS
ACTION_LIST = [
    # client actions
    'authenticate',
    'quit',
    'on_chat',
    'on_group',
    'create_group',
    'join_group',
    'leave_group',
    'p2p',
    'presence',
    'get_contacts',
    'add_contact',
    'del_contact',
    # server actions
    'probe',
    'on_chat',
    'on_group',
]
