""" Серверная часть """
import sys

from PyQt5.QtWidgets import QApplication
from select import select
import socket
import threading
from lib.processors.message_sender import MessageSender
from lib.variables import *
from lib.processors.receive_message_processor import MessageSplitter
from gui.server_gui import MainWindow


class Server:
    def __init__(self, SERVER_ADDR):
        self.logger = logging.getLogger('server_log')
        self.SERVER_ADDR = SERVER_ADDR
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []
        self.msg_splitter = MessageSplitter()
        self.message_sender = MessageSender()
        self.send_buffer = self.message_sender.send_buffer

    def broadcast(self, message):
        """ отправляет сообщение всем участникам """
        for client in self.clients:
            client.send(message)

    def disconnect_socket(self, sock):
        """ отключает сокет """
        # TODO как получить адрес клиента если он отключился?
        self.logger.info('Client disconnected')
        index = self.clients.index(sock)
        sock.close()
        self.clients.remove(sock)
        # self.broadcast(f'Client {nickname} disconnected!'.encode(ENCODING_FORMAT))

    def clients_read(self, r_sockets):
        """ читает данные из сокетов, от которыз поступили запросы и скармливает их на обработку в message splitter"""
        requests = {}
        for sock in r_sockets:
            try:
                data = sock.recv(MAX_MSG_SIZE)  # читаем запакованные через struct данные

                # скармливаем данные с целью выполнить действия и сформировать ответ клиентам
                self.msg_splitter.feed(data)
                requests[sock] = self.send_buffer.data[0]
                self.send_buffer.bytes_sent()
            except:
                # удаляем сокет из переченя если клиент отключился
                self.disconnect_socket(sock)
        return requests

    def clients_write(self, responses: dict, w_sockets):
        """ направляет ответы в сокеты, доступные для записи """
        try:
            for sock in w_sockets:
                for author_sock, response in responses.items():
                    if author_sock == sock:
                        sock.send(response)
        except:
            # удаляем сокет из переченя если клиент отключился
            self.disconnect_socket(sock)

    def authenticate_client(self, client_sock, addr):
        """ запрос и обработка результата авторизации пользователя при подключении к серверу """
        self.logger.info('Try to authenticate client %s', str(addr))

        client_sock.send('AUTH'.encode(ENCODING_FORMAT))  # запрашиваем действие авторизации
        auth_data = client_sock.recv(MAX_MSG_SIZE)  # получаем ответ

        self.msg_splitter.feed(auth_data)  # отправляет данные на обработку
        client_sock.send(self.send_buffer.data[0])  # читаем буфер ответов после обработки и направляем ответ клиенту
        self.send_buffer.bytes_sent()  # удаляем прочитанный ответ из буфера
        self.clients.append(client_sock)

    def get_client_contacts(self, client_sock, addr):
        """ запрос к БД и отправка списка контактов клиенту """
        self.logger.info('Getting client contact list %s', str(addr))

        client_sock.send('GET_CONTACTS'.encode(ENCODING_FORMAT))
        request_data = client_sock.recv(MAX_MSG_SIZE)

        self.msg_splitter.feed(request_data)
        client_sock.send(self.send_buffer.data[0])
        self.send_buffer.bytes_sent()

    def run(self):
        """ основной поток обработки входящих соединений """
        print('Server is listening...')

        self.server.bind(self.SERVER_ADDR)
        self.server.listen(MAX_CONNECTIONS)
        self.server.settimeout(0.2)

        while True:
            try:
                client, addr = self.server.accept()
                print(f'Connected with {str(addr)}')

                # self.authenticate_client(client_sock=client, addr=addr)
                # self.get_client_contacts(client_sock=client, addr=addr)
            except ValueError as e:
                print(e)
            except OSError as e:
                pass
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                print(e)
            finally:
                r_sockets = []
                w_sockets = []
                try:
                    r_sockets, w_sockets, e = select(self.clients, self.clients, [], 0)
                except:
                    pass  # ничего не делать если клиент отключился
                responses = self.clients_read(r_sockets)
                if responses:
                    self.clients_write(responses, w_sockets)


if __name__ == "__main__":
    server = Server(SERVER_ADDR)
    serv_thr = threading.Thread(target=server.run)
    serv_thr.start()

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
