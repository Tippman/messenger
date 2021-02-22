# Программа сервера для получения приветствия от клиента и отправки ответа
from contextlib import closing
from socket import *
import click
import json
import time


@click.command()
@click.option('--a', help='server IP address')
@click.option('--p', default=7777, help='server TCP port (default - 7777)')
def connect(a, p):
    with socket(AF_INET, SOCK_STREAM) as s:  # Создает сокет TCP
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Чтобы не занимался порт при вываливании ошибки
        s.bind((a, p))  # Присваивает порт
        s.listen()

        while True:
            client, addr = s.accept()
            with closing(client) as cl:
                request = cl.recv(640)
                data = json.loads(request)

                print(
                    "Сообщение: ",
                    data['action'],
                    ", было отправлено клиентом: ",
                    data['user']['account_name'],
                    data['time'],
                    addr,
                )

                response = {
                    'response': 200,
                    'time': time.ctime(time.time()),
                    'alert': 'Success connection established!'
                }
                cl.send(json.dumps(response).encode("utf-8"))


if __name__ == '__main__':
    connect()
