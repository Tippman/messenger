"""Модуль создания структуры БД и наполения ее тестовыми данными."""
import hashlib
import sqlite3

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.client_db import *
from lib.processors.message_dataclasses import AddContactMessage
from lib.processors.message_handlers import ServerMessageHandler
from lib.variables import ENCODING_FORMAT, ENGINE, HASH_FUNC, SALT


def get_hex_password(raw_password: str) -> hex:
    """Возвращает hex, полученный из *raw_password*.

    :param raw_password: Строка-пароль.
    :return: Hex пароля, полученный через hashlib.pbkdf2_hmac.
    """
    return hashlib.pbkdf2_hmac(HASH_FUNC,
                               bytes(raw_password, encoding=ENCODING_FORMAT),
                               bytes(SALT, encoding=ENCODING_FORMAT),
                               100000).hex()


def main():
    """Создание БД, структуры таблиц, сессии и наполнение тестовыми данными."""
    Base.metadata.create_all(ENGINE)

    Session = sessionmaker(bind=ENGINE)
    session = Session()

    client_storage = ClientStorage(session)
    test_users = {
        'tippman': get_hex_password('s1234'),
        'login2': get_hex_password('2'),
        'login3': get_hex_password('3'),
        'login4': get_hex_password('4'),
        'login5': get_hex_password('5'),
        'login6': get_hex_password('6'),
    }

    test_contacts = [
        AddContactMessage(action='add_contact', time='None', author='tippman', target_login='login3'),
        AddContactMessage(action='add_contact', time='None', author='tippman', target_login='login5'),
        AddContactMessage(action='add_contact', time='None', author='login3', target_login='tippman'),
        AddContactMessage(action='add_contact', time='None', author='login3', target_login='login5'),
        AddContactMessage(action='add_contact', time='None', author='login4', target_login='tippman'),
    ]

    try:
        for user in test_users.items():
            client_storage.add_client(login=user[0], hash_password=user[1])
        for contact in test_contacts:
            current_client = client_storage.get_client(contact.author)
            target_client = client_storage.get_client(contact.target_login)

            if target_client not in current_client.contacts.all() and target_client != current_client:
                current_client.contacts.append(target_client)

    except IntegrityError:
        print('test users already created')
    finally:
        print(f'{len(test_users.items())} users created')
        session.commit()
        session.close()


if __name__ == '__main__':
    main()
