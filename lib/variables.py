""" Константы используемые в файлах проекта"""
import logging

DEFAULT_PORT = 7777  # порт по умолчанию
DEFAULT_IP = '127.0.0.1'  # IP адрес по умолчанию
SERVER_ADDR = (DEFAULT_IP, DEFAULT_PORT)  # адрес по умолчанию
MAX_CONNECTIONS = 5  # максимальная очередь подключений
MAX_MSG_SIZE = 1022  # max длина сообщения в байтах
ENCODING_FORMAT = 'utf-8'  # кодировка
HEADER_LENGTH_BYTES = '>h'  # длина заголовка сообщения - 2 байта
PACK_FORMAT = f'{HEADER_LENGTH_BYTES}{MAX_MSG_SIZE}s'

# ACTIONS
ACTION_LIST = [
    'authenticate',
    'quit',
    'on chat',
    'on group',
    'p2p',
    'presence',
    'probe',
]


