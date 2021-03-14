import click
from socket import socket, AF_INET, SOCK_STREAM

from messenger.client import Client
from messenger.client_soket import ClientSoket

ENCODING = 'utf-8'


@click.command()
@click.option('--addr', help='server IP address')
@click.option('--port', default=7777, help='server TCP port (default - 7777)')
def main(addr, port):
    with socket(AF_INET, SOCK_STREAM) as s:  # Создать сокет TCP
        s.connect(('127.0.0.1', 7777))  # Соединиться с сервером
        client_socket = ClientSoket(s)
        client = Client(client_socket=client_socket, account_name='tippman')
        client.authenticate(password='qwerty12')
        client.get_response()


if __name__ == '__main__':
    main()
