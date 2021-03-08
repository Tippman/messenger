# Программа сервера для получения приветствия от клиента и отправки ответа
from contextlib import closing
from socket import *
import click
import json
import time
import logging
import log.server_log_config

ENCODING = 'utf-8'
logger = logging.getLogger('messenger.server')


@click.command()
@click.option('--a', help='server IP address')
@click.option('--p', default=7777, help=f'server TCP port (default - 7777)')
def main(a, p):
    with socket(AF_INET, SOCK_STREAM) as s:  # Создает сокет TCP
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Чтобы не занимался порт при вываливании ошибки
        s.bind((a, p))  # Присваивает порт
        s.listen()

        while True:
            client, addr = s.accept()
            with closing(client):
                request = client.recv(10000)
                request_str = request.decode(ENCODING)
                data = json.loads(request_str)
                print(
                    "Сообщение: ", request_str,
                    ", было отправлено клиентом: ", addr,
                )
                logger.info('server get message, action - %s', data['action'])

                if 'action' in data and data['action'] == 'authenticate':
                    response = {
                        'response': 200,
                        'time': time.time(),
                        'alert': 'Success connection established!'
                    }
                    client.send(json.dumps(response).encode(ENCODING))
                    logger.info('success authorise user %s', data['user']['account_name'])
                elif 'action' in data and data['action'] == 'quit':
                    print('Client disconnected')
                    logger.info('user %s disconected', data['user']['account_name'])
                    break


if __name__ == '__main__':
    main()
