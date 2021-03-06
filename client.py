import click
from socket import *
import time
import json


@click.command()
@click.option('--addr', help='server IP address')
@click.option('--port', default=7777, help='server TCP port (default - 7777)')
def connect(addr, port):
    """Establish a connection to the server"""
    with socket(AF_INET, SOCK_STREAM) as s:  # Создать сокет TCP
        s.connect((addr, port))  # Соединиться с сервером

        request = {
            'action': 'presence',
            'time': time.ctime(time.time()),
            'type': 'status',
            'user': {
                "account_name": "tippman",
                "status": "Yep, I am here!"
            },
        }
        s.send(json.dumps(request).encode("utf-8"))

        response = s.recv(640)
        data = json.loads(response)

        print(f'Сообщение от сервера: {data["response"]} {data["alert"]}, длиной {len(response)} байт')


if __name__ == '__main__':
    connect()
