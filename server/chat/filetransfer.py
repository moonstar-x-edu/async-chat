import socket
import os
from threading import Thread
from .chatserver import ChatServer, TAG_FILE

DEFAULT_FILE_TRANSFER_PORT = 20023
DEFAULT_BUFFER_SIZE = 1024
DEFAULT_MAX_CONNECTIONS = 100

FILES_LOCATION = os.path.abspath(f'{os.path.realpath(os.path.dirname(__file__))}/../files')


class FileTransferConnection(Thread):
    def __init__(self, file_server, client_socket: socket, client_address: tuple):
        Thread.__init__(self)
        self.daemon = True

        self.file_server = file_server
        self.socket = client_socket
        self.address = client_address

    def run(self):
        operation, source_user, destination_user, filename, file_size = self.request_header()

        if not self.is_header_valid(operation, source_user, destination_user):
            self.send_message('ERROR')
            self.file_server.close_connection(self)
            return

        self.send_message('OK')

        if operation == 'UP':
            self.handle_upload(source_user, destination_user, filename, file_size)
        else:
            self.handle_download(filename)

        self.file_server.close_connection(self)

    def request_header(self) -> tuple:
        header_received = self.receive_message()

        self.log('INFO', f'Received header: {header_received}')

        header_split = header_received.split(';')
        operation = header_split[0]
        source_user = header_split[1]
        destination_user = header_split[2]
        filename = header_split[3]
        file_size_str = header_split[4]
        file_size = int(file_size_str) if file_size_str else -1

        return operation, source_user, destination_user, filename, file_size

    def is_header_valid(self, operation: str, source_user: str, destination_user: str) -> bool:
        if operation != 'UP' and operation != 'DOWN':
            return False

        if operation == 'UP':
            if self.file_server.chat_server.get_connection_by_username(source_user) is None:
                return False

            if self.file_server.chat_server.get_connection_by_username(destination_user) is None:
                return False

        return True

    def handle_upload(self, source_user: str, destination_user: str, filename: str, file_size: int):
        file_path = os.path.abspath(f'{FILES_LOCATION}/{filename}')
        uploaded = 0

        with open(file_path, 'wb') as file:
            while True:
                part_content = self.receive_part()

                if part_content is None or len(part_content) == 0:
                    break

                file.write(part_content)

                uploaded += self.file_server.buf_size
                self.log('UPLOAD', f'Received {int(100 * uploaded / file_size)}')

        self.log('UPLOAD', f'File reception finished. Notifying {destination_user}')

        self.file_server.chat_server\
            .get_connection_by_username(destination_user)\
            .send_to_socket(TAG_FILE, f'{source_user};{filename};{file_size}')

    def handle_download(self, filename: str):
        file_path = os.path.abspath(f'{FILES_LOCATION}/{filename}')

        if not os.path.exists(file_path):
            self.send_message('ERROR')
            return

        file_size = os.path.getsize(file_path)
        downloaded = 0

        with open(file_path, 'rb') as file:
            while True:
                part_content = file.read(self.file_server.buf_size)

                if len(part_content) == 0:
                    break

                self.send_part(part_content)

                downloaded += self.file_server.buf_size
                self.log('DOWNLOAD', f'Transferred {int(100 * downloaded / file_size)}%')

        self.log('DOWNLOAD', f'File transfer finished.')

    def send_part(self, part_content: bytes):
        if self.socket is None:
            raise Exception('No socket connection is available to this file uploader.')

        self.socket.sendall(part_content)

    def receive_part(self) -> bytes:
        if self.socket is None:
            raise Exception('No socket connection is available to this file downloader.')

        return self.socket.recv(self.file_server.buf_size)

    def send_message(self, message: str):
        if self.socket is None:
            raise Exception('No socket connection is available to this file uploader.')

        self.socket.sendall(message.encode('ASCII'))

    def receive_message(self) -> str:
        if self.socket is None:
            raise Exception('No socket connection is available to this file uploader.')

        data = self.socket.recv(self.file_server.buf_size)

        if not data:
            raise Exception('No data received on socket. Was the connection interrupted?')

        return data.decode('ASCII')

    def log(self, label: str, message: str):
        print(f'(FILE SERVER - {self.address}) : [{label}] - {message}')


class FileTransferServer(Thread):
    def __init__(self, chat_server: ChatServer, port: int, **kwargs):
        Thread.__init__(self)
        self.daemon = True

        self.chat_server = chat_server
        self.port = port
        self.buf_size = kwargs.get('buffer_size') or DEFAULT_BUFFER_SIZE
        self.max_connections = kwargs.get('max_connections') or DEFAULT_MAX_CONNECTIONS

        self.connections = dict()
        self.socket = None

    def run(self):
        self.listen_for_connections()

    def initialize(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', self.port))
        self.socket.listen(self.max_connections)

        self.log('INFO', f'File server started on port {self.port}')

    def listen_for_connections(self):
        if self.socket is None:
            raise Exception('No socket connection is available to this file server.')

        while True:
            try:
                client_socket, client_address = self.socket.accept()

                connection = FileTransferConnection(self, client_socket, client_address)
                self.connections[client_address] = connection
                connection.log('INFO', 'Initializing file transfer.')
                connection.start()

            except Exception or KeyboardInterrupt:
                break

        self.log('INFO', 'Closing file server...')
        self.close_server()

    def close_connection(self, connection: FileTransferConnection):
        if self.connections.get(connection.address) is None:
            return

        connection.socket.close()
        connection.log('INFO', 'Closed file transfer connection.')

        del self.connections[connection.address]

    def close_server(self):
        if self.socket is None:
            raise Exception('No socket connection is available to this file server.')

        self.socket.close()
        for connection in self.connections.values():
            connection.socket.close()

    @staticmethod
    def log(label: str, message: str):
        print(f'(FILE SERVER): [{label}] - {message}')
