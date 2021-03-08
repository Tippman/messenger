import click
from socket import *
import time
import json

from messenger.client import Client
from messenger.client_soket import ClientSoket
from messenger.messages import Authentificate

ENCODING = 'utf-8'


@click.command()
@click.option('--addr', help='server IP address')
@click.option('--port', default=7777, help='server TCP port (default - 7777)')
def main(addr, port):
    with socket(AF_INET, SOCK_STREAM) as s:  # Создать сокет TCP
        s.connect((addr, port))  # Соединиться с сервером
        client_soket = ClientSoket(s)
        client = Client(client_socket=client_soket, account_name='tippman')
        client.authenticate(password='qwerty12')
        server_response = client.get_response()
        print(server_response)

if __name__ == '__main__':
    main()

# def connect(addr, port):
#     """Establish a connection to the server"""
#     with socket(AF_INET, SOCK_STREAM) as s:  # Создать сокет TCP
#         s.connect((addr, port))  # Соединиться с сервером
#
#         request = {
#             'action': 'authenticate',
#             'time': time.ctime(time.time()),
#             'user': {
#                 "account_name": "tippman",
#                 "password": "qwerty1234"
#             },
#         }
#         s.send(json.dumps(request).encode(ENCODING))
#
#         response = s.recv(640)
#         response_str = response.decode(ENCODING)
#         data = json.loads(response_str)
#         print(f'Сообщение от сервера: {data["response"]} {data["alert"]}, длиной {len(response)} байт')
#
#
# if __name__ == '__main__':
#     connect()
