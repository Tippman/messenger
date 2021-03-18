from contextlib import closing
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import click
import json
import time
import logging
from select import select
import log.server_log_config

ENCODING = 'utf-8'
logger = logging.getLogger('messenger.server')


def disconnect_client(sock, all_clients):
    # print(f"Клиент {sock.fileno()} {sock.getpeername()} отключился")
    sock.close()
    all_clients.remove(sock)


def read_requests(r_clients, all_clients):
    responses = {}  # Словарь ответов сервера вида {сокет: запрос}

    for sock in r_clients:
        try:
            data = sock.recv(1024).decode(ENCODING)
            responses[sock] = data
            print(responses[sock])
            # logger.info('server get message, action - %s', responses[sock]['action'])
        except Exception as e:
            logger.error('%s', e)
            disconnect_client(sock, all_clients)
            raise

    return responses


def write_responses(requests, w_clients, all_clients):
    for sock in w_clients:
        for recv_sock, data in requests.items():
            if sock is recv_sock:
                continue

            try:
                resp = data.encode(ENCODING)
                sock.send(resp)
            except:  # Сокет недоступен, клиент отключился
                disconnect_client(sock, all_clients)


@click.command()
@click.option('--a', help='server IP address')
@click.option('--p', default=7777, help=f'server TCP port (default - 7777)')
def main(a, p):
    clients = []

    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    try:
        s.bind((a, p))
        s.listen()
        s.settimeout(0.2)  # Таймаут для операций с сокетом
        while True:
            try:
                conn, addr = s.accept()  # Проверка подключений
            except OSError:
                pass  # timeout вышел
            else:
                logger.info("Получен запрос на соединение от %s", addr)
                # print(f"Получен запрос на соединение от {addr}")
                clients.append(conn)
            finally:
                # Проверить наличие событий ввода-вывода
                wait = 0
                r = []
                w = []
                try:
                    r, w, e = select(clients, clients, [], wait)
                except:
                    pass  # Ничего не делать, если какой-то клиент отключился

                requests = read_requests(r, clients)  # Сохраним запросы клиентов
                write_responses(
                    requests, w, clients
                )  # Выполним отправку ответов клиентам
    finally:
        for sock in clients:
            sock.close()
        s.close()

        # with closing(client):
        #     request = client.recv(10000)
        #     request_str = request.decode(ENCODING)
        #     data = json.loads(request_str)
        #     logger.info('server get message, action - %s', data['action'])
        #
        #     if 'action' in data and data['action'] == 'authenticate':
        #         response = {
        #             'response': 200,
        #             'time': time.time(),
        #             'alert': 'Success connection established!'
        #         }
        #         client.send(json.dumps(response).encode(ENCODING))
        #         logger.info('success authorise user %s', data['user']['account_name'])
        #     elif 'action' in data and data['action'] == 'quit':
        #         logger.info('user %s disconnected', data['user']['account_name'])
        #         break


if __name__ == '__main__':
    main()
