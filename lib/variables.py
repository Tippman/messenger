""" Константы используемые в файлах проекта"""
import logging

DEFAULT_PORT = 7777  # порт по умолчанию
DEFAULT_IP = '127.0.0.1'  # IP адрес по умолчанию
MAX_CONNECTIONS = 5  # максимальная очередь подключений
PACKAGE_LENGTH = 1024  # длина сообщения в байтах
ENCODING = 'utf-8'  # кодировка
SERVER_TIMEOUT = 1

# Протокол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'


# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
AUTH = 'authenticate'
ALERT = 'alert'
MSG = 'msg'
MSG_TEXT='msg_text'
LISTEN = 'listen' # ключ для словаря, отправка от клиента запрос на прослушивание
EXIT = 'exit'
WHO='who'

CLIENT_LISTEN = False  # используется для определения, клиент пишет или слушает

ERR200 = '200:OK'
ERR400 = '400:Bad request'

RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {RESPONSE: 400,ERROR: None}

# настройка логирования
LOG_LEVEL = logging.DEBUG
LOG_FORMATTER = '%(asctime)s %(levelname)s %(filename)s %(message)s'

