""" Конфиг серверного логгера"""

import logging
import logging.config
import os
from pathlib import Path

from icecream import ic

BASE_DIR = Path(__file__).resolve().parent.parent

LOGGER_FILENAMES = {
    'SERVER_LOG_FILENAME': 'server_log.log',
    'CLIENT_LOG_FILENAME': 'client_log.log',
    'SERVER_ADMIN_APP_LOG': 'server_admin_app_log.log',
    'CLIENT_LOGIN_APP_LOG': 'client_login_app_log',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'basic': {
            'format': '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
        },
    },
    'handlers': {
        'server_log': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'filename': f'{BASE_DIR}/logs/log_files/{LOGGER_FILENAMES["SERVER_LOG_FILENAME"]}',
            'encoding': 'utf-8',
            'formatter': 'basic',
        },
        'client_log': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'filename': f'{BASE_DIR}/logs/log_files/{LOGGER_FILENAMES["CLIENT_LOG_FILENAME"]}',
            'encoding': 'utf-8',
            'formatter': 'basic',
        },
        'server_admin_app_log': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'filename': f'{BASE_DIR}/logs/log_files/{LOGGER_FILENAMES["SERVER_ADMIN_APP_LOG"]}',
            'encoding': 'utf-8',
            'formatter': 'basic',
        },
        'client_login_app_log': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'filename': f'{BASE_DIR}/logs/log_files/{LOGGER_FILENAMES["CLIENT_LOGIN_APP_LOG"]}',
            'encoding': 'utf-8',
            'formatter': 'basic',
        },
    },
    'loggers': {
        'server_log': {
            'handlers': ['server_log'],
            'level': 'DEBUG',
        },
        'client_log': {
            'handlers': ['client_log'],
            'level': 'DEBUG',
        },
        'server_admin_app_log': {
            'handlers': ['server_admin_app_log'],
            'level': 'DEBUG',
        },
        'client_login_app_log': {
            'handlers': ['client_login_app_log'],
            'level': 'DEBUG',
        },

    }
}

try:
    logging.config.dictConfig(LOGGING)
except ValueError:
    try:
        os.mkdir(f'{BASE_DIR}/logs/log_files/')
    except FileExistsError:
        pass

    for key, filename in LOGGER_FILENAMES.items():
        with open(f'{BASE_DIR}/logs/log_files/{filename}', 'w', encoding='utf-8'):
            pass
    logging.config.dictConfig(LOGGING)
