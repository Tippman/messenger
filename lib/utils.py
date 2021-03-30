""" общие утилиты """

import json
import socket
import sys
from lib.errors import IncorrectDataRecivedError, NonDictInputError
from lib.variables import PACKAGE_LENGTH, ENCODING, DEFAULT_PORT, DEFAULT_IP, MAX_CONNECTIONS, CLIENT_LISTEN


def validate_ip(ip_str):
    """ Проверка что строка является действительным адресом IPv4.
    Возавращает True / False
    :param ip_str:
    :return:
    """
    tmp_str = ip_str.split('.')
    if len(tmp_str) != 4:
        return False
    for el in tmp_str:
        if not el.isdigit():
            return False
        i = int(el)
        if i < 0 or i > 255:
            return False
    return True


def validate_port(ip_rort):
    """ Проверка что строка может являться разрешенным портом
    Возавращает True / False
    :param ip_rort:
    :return:
    """
    try:
        ip_rort = int(ip_rort)
        if ip_rort < 1025 or ip_rort > 65535:
            return False
        else:
            return True
    except:
        return False


def server_settings():
    '''
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    server.py -i(or -ip) 192.168.1.125 -p(or -port) 9999
    :return:
    '''
    client_listen = CLIENT_LISTEN
    try:
        # ищем в строке запуска тип клиента -l(listen) для клиентов, которые будут в роли "слушателя"
        if '-l' in sys.argv:
            # print("client_listen=====True")
            client_listen = True

        # ищем в строке запуска ip
        if '-ip' in sys.argv:
            server_address = sys.argv[sys.argv.index('-ip') + 1]
        elif '-i' in sys.argv:
            server_address = sys.argv[sys.argv.index('-i') + 1]
        else:
            server_address = DEFAULT_IP
        if not validate_ip(server_address) and server_address != '':
            raise ValueError

        # ищем в строке запуска порт
        if '-p' in sys.argv:
            server_port = int(sys.argv[sys.argv.index('-p') + 1])
        elif '-port' in sys.argv:
            server_port = int(sys.argv[sys.argv.index('-port') + 1])
        else:
            server_port = DEFAULT_PORT
        if not validate_port(server_port):
            raise ValueError


    except ValueError:
        print('Некорректный адрес. Запуск скрипта должен быть: ****.py -i(or -ip) XXX.XXX.XXX.XXX -p(or -port) 9999')
        sys.exit(1)
    return [server_address, server_port, client_listen]


def create_socket():
    """ создаем сокет для соединения """
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return soc


def get_message(client):
    '''
    Утилита приёма и декодирования сообщения
    принимает байты выдаёт словарь, если принято что-то другое отдаёт ошибку значения
    :param client:
    :return:
    '''

    response_bytes = client.recv(PACKAGE_LENGTH)
    if isinstance(response_bytes, bytes):
        json_response = response_bytes.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise IncorrectDataRecivedError  # ValueError
    raise IncorrectDataRecivedError  # ValueError


def send_message(sock_obj, message):
    '''
    Утилита кодирования и отправки сообщения
    принимает словарь и отправляет его
    :param sock_obj:
    :param message:
    :return:
    '''
    if not isinstance(message, dict):
        raise NonDictInputError
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock_obj.send(encoded_message)
