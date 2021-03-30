""" серверная часть """
import json
import logging
import select
import time
import sys
import logs.config_server_log
from lib.variables import *
from lib.utils import server_settings, create_socket, get_message, send_message
from logs.decoration_log import log

SERVER_LOGGER = logging.getLogger('server')


@log
def client_message_handler(message, messages_list, client, clients, names):
    '''
    Обработчик сообщений от клиентов, принимает словарь - сообщение от клинта,
    проверяет корректность, отправляет словарь-ответ для клиента с результатом приёма.
    :param message:
    :param messages_list:
    :param client:
    :return:
    '''
    SERVER_LOGGER.debug(f'функция разбора message от клиента: {message}')
    if ACTION not in message:
        SERVER_LOGGER.error(f"сообщение от клиента не содержит обязательного поля ACTION: {message}")
        print(f"сообщение от клиента не содержит обязательного поля ACTION: {message}")
        send_message(client, {RESPONSE: 400, ERROR: ERR400})
        return
    elif TIME not in message:
        SERVER_LOGGER.error(f"сообщение от клиента не содержит обязательного поля TIME: {message}")
        print(f"сообщение от клиента не содержит обязательного поля TIME: {message}")
        send_message(client, {RESPONSE: 400, ERROR: ERR400})
        return
    elif ACTION in message and message[ACTION] == PRESENCE and TIME in message and message[USER][
        ACCOUNT_NAME] == 'Guest':
        SERVER_LOGGER.debug(f"сформировано PRESENCE сообщение:{message}")
        send_message(client, {RESPONSE: 200, ERROR: ERR200, MSG: str(f"Welcome, {message[USER][ACCOUNT_NAME]}")})
        return
    elif ACTION in message and message[ACTION] == AUTH and TIME in message and USER in message \
            and message[USER][ACCOUNT_NAME] != 'Guest':
        if str(message[USER][ACCOUNT_NAME]).lower() not in str(names.keys()).lower():  # нет такого, можно регать
            SERVER_LOGGER.debug(f"сформировано AUTH сообщение: {message}. Пользователь занесен в список")
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, {RESPONSE: 200, ERROR: ERR200, MSG: str(f"Welcome, {message[USER][ACCOUNT_NAME]}")})
            return
        else:
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя уже занято.'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    elif ACTION in message and message[ACTION] == MSG and DESTINATION in message and TIME in message \
            and SENDER in message and MSG_TEXT in message:
        SERVER_LOGGER.debug(f"сформировано MSG сообщение: {message}")
        messages_list.append((message))
        return
    elif ACTION in message and message[ACTION] == WHO and TIME in message:
        SERVER_LOGGER.debug(f"сформировано WHO сообщение: {message}")
        message[DESTINATION] = message[SENDER]  # отправить список самому себе
        all_names = ''
        for el in names:
            all_names += all_names + ' | ' + el
        all_names = f"пользователи в сети:\n{all_names[3:]}"
        message[MSG_TEXT] = all_names
        messages_list.append((message))
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        SERVER_LOGGER.info(f"пользователь {message[ACCOUNT_NAME]} вышел")
        print(f"пользователь {message[ACCOUNT_NAME]} вышел")
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    else:
        SERVER_LOGGER.error(f"функция разбора message от клиента, ни одно из условий не подошло: {message}")
        print(f"функция разбора message от клиента, ни одно из условий не подошло: {message}")
        response = RESPONSE_400
        response[ERROR] = 'Запрос некорректен.'
        send_message(client, response)
        return


@log
def process_message(message, names, listen_socks):
    """
    Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
    список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
    :param message:
    :param names:
    :param listen_socks:
    :return:
    """
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        SERVER_LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                           f'от пользователя {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(
            f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')


@log
def start_server():
    srv_settings = server_settings()
    server_address = srv_settings[0]
    server_port = srv_settings[1]

    transport = create_socket()
    transport.bind((server_address, server_port))
    transport.settimeout(SERVER_TIMEOUT)
    transport.listen(MAX_CONNECTIONS)

    print(f"server start on: {server_address}:{server_port}")
    SERVER_LOGGER.info(f"server started on {server_address}:{server_port}")

    clients = []  # список клиентов
    messages = []  # список сообщений

    names = dict()  # словарь зарегистрированных пользователей

    while True:
        try:
            client, client_address = transport.accept()
            SERVER_LOGGER.debug(f'client | {client_address}')
        except OSError:
            pass
        else:
            print(f"Получен запрос на соединение от {str(client_address)}")
            SERVER_LOGGER.info(f"установлено соедниение с клиентом {client_address}")
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []

        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    client_message_handler(get_message(client_with_message), messages, client_with_message, clients,
                                           names)
                except Exception:
                    SERVER_LOGGER.info(f"клиент {client_with_message.getpeername()} отключился")
                    print(f"клиент {client_with_message.getpeername()} отключился")
                    clients.remove(client_with_message)
        for i in messages:
            try:
                process_message(i, names, send_data_lst)
            except Exception:
                SERVER_LOGGER.info(f'Связь с клиентом  {i[DESTINATION]} потеряна')
                clients.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
            messages.clear()


if __name__ == '__main__':
    start_server()
