""" Серверная часть """
import sys
from queue import Queue

from PyQt5.QtWidgets import QApplication
from select import select
import socket
import threading

from icecream import ic
from sqlalchemy.orm import sessionmaker

from db.client_db import ClientStorage, ClientHistoryStorage
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
        self.nicknames = []
        self.msg_splitter = MessageSplitter()
        self.message_sender = MessageSender()
        self.send_buffer = self.message_sender.send_buffer
        self.server_queue = Queue()

    def broadcast(self, message):
        """ отправляет сообщение всем участникам """
        for client in self.clients:
            client.send(message)

    def disconnect_socket(self, sock):
        """ отключает сокет """
        # TODO как получить адрес клиента если он отключился?
        self.logger.info('Client disconnected')
        # index = self.clients.index(sock)
        sock.close()
        if sock in self.clients:
            ind = self.clients.index(sock)
            login = self.nicknames[ind]
            self.nicknames.remove(login)
            self.clients.remove(sock)

        # self.broadcast(f'Client {nickname} disconnected!'.encode(ENCODING_FORMAT))

    def clients_read(self, r_sockets):
        """ читает данные из сокетов, от которыз поступили запросы и скармливает их на обработку в message splitter"""
        requests = {}
        for sock in r_sockets:
            try:
                data = sock.recv(MAX_MSG_SIZE)  # читаем запакованные через struct данные

                # скармливаем данные с целью выполнить действия и сформировать ответ клиентам
                self.msg_splitter.feed(data=data, server_queue=self.server_queue)
                requests[sock] = self.send_buffer.data[0]
                self.send_buffer.bytes_sent()
            except IndexError:
                # если буфер отправки пуст - ничего не делаем
                pass
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

    @staticmethod
    def create_db_connection():
        """ return session """
        Session = sessionmaker(bind=ENGINE)
        session = Session()
        return session

    def authenticate_client(self, client_sock, addr):
        """ запрос и обработка результата авторизации пользователя при подключении к серверу """
        self.logger.info('Try to authenticate client %s', str(addr))

        client_sock.send('AUTH'.encode(ENCODING_FORMAT))  # запрашиваем действие авторизации
        auth_data = client_sock.recv(MAX_MSG_SIZE)  # получаем ответ. первый - словарь-запрос авторизации
        client_login = client_sock.recv(MAX_MSG_SIZE).decode(
            ENCODING_FORMAT)  # получаем ответ. второй - логин пользователя

        self.msg_splitter.feed(auth_data)  # отправляет данные на обработку
        client_sock.send(self.send_buffer.data[0])  # читаем буфер ответов после обработки и направляем ответ клиенту
        self.send_buffer.bytes_sent()  # удаляем прочитанный ответ из буфера

        # делаем запрос в БД:
        #   если авторизация прошла успешно -
        #   добавляем сокет в список подключенных и запрашиваем список контактов
        client_storage = ClientStorage(self.create_db_connection())
        if client_storage.get_client(client_login).is_auth:
            self.clients.append(client_sock)
            self.nicknames.append(client_login)
            self.get_client_contacts(client_sock, addr)
        else:
            self.disconnect_socket(client_sock)

    def get_client_contacts(self, client_sock, addr):
        """ запрос к БД и отправка списка контактов клиенту """
        self.logger.info('Getting client contact list %s', str(addr))

        client_sock.send('GET_CONTACTS'.encode(ENCODING_FORMAT))
        request_data = client_sock.recv(MAX_MSG_SIZE)

        self.msg_splitter.feed(request_data)
        client_sock.send(self.send_buffer.data[0])
        self.send_buffer.bytes_sent()

    def server_queue_handler(self, stopper):
        """ обработка очереди сервера (наполняется из message_handler) """
        while not stopper.is_set():
            if not self.server_queue.empty():
                ic('que not empty')
                queue_item = self.server_queue.get_nowait()
                if isinstance(queue_item, dict):
                    try:
                        if queue_item['action'] == 'p2p':
                            sock_ind = self.nicknames.index(queue_item['target_login'])
                            target_sock = self.clients[sock_ind]
                            target_ip, target_port = target_sock.getsockname()
                            self.server.sendto(
                                queue_item['message'].encode(ENCODING_FORMAT),
                                (target_ip, target_port)
                            )
                    except KeyError:
                        self.logger.debug('Error while handling server queue. Key err.')
                    except ValueError:
                        self.logger.debug('target is offline')

    def run(self, event):
        """ основной поток обработки входящих соединений """
        print('Server is listening...')

        self.server.bind(self.SERVER_ADDR)
        self.server.listen(MAX_CONNECTIONS)
        self.server.settimeout(0.2)

        server_queue_thr = threading.Thread(target=self.server_queue_handler, args=(event,))
        server_queue_thr.start()

        while not event.is_set():
            try:
                client, addr = self.server.accept()
                print(f'Connected with {str(addr)}')
                self.authenticate_client(client_sock=client, addr=addr)
            except OSError:
                pass
            except KeyboardInterrupt:
                event.set()
            except Exception as e:
                print(e)
            finally:
                r_sockets = []
                w_sockets = []
                try:
                    r_sockets, w_sockets, e = select(self.clients, self.clients, [], 0)
                except:
                    self.clients.remove(client)  # если клиент отключился
                responses = self.clients_read(r_sockets)
                if responses:
                    self.clients_write(responses, w_sockets)


if __name__ == "__main__":
    server = Server(SERVER_ADDR)
    server_kill = threading.Event()
    serv_thr = threading.Thread(target=server.run, args=(server_kill,))
    serv_thr.start()

    # app = QApplication(sys.argv)
    # mw = MainWindow()
    # mw.show()
    # app.exec_()
    #
    # server_kill.set()
    # serv_thr.join()
