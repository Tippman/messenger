""" Константы используемые в файлах проекта"""
import logging
import ipaddress
from pathlib import Path

from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parent.parent

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
HEADER_PORT_BYTES = 'i'  # длина заголовка PORT - 4 байта
PACK_FORMAT = f'>{HEADER_MSG_LENGTH_BYTES}{HEADER_IP_BYTES}{HEADER_PORT_BYTES}{MAX_MSG_SIZE - 10}s'
SMALL_PACK_FORMAT = f'>{HEADER_MSG_LENGTH_BYTES}{MAX_MSG_SIZE - 2}s'

# database settings
ENGINE = create_engine(f'sqlite:////{BASE_DIR}/messenger.sqlite3', echo=False)
ENGINE_PATH = 'sqlite:///../messenger.sqlite3'

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
    'add_new_client',
    # server actions
    'probe',
    'on_chat',
    'on_group',
]

# TODO вынести соль в переменную окрудения сервера
SALT = 'secret_salt'
HASH_FUNC = 'sha256'
