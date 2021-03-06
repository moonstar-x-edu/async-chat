import socket
import sys
from utils.events import EventEmitter
from utils.schedulers import IntervalExecutor
from .filetransfer import FileTransferUploader, FileTransferDownloader

DEFAULT_BUFFER_SIZE = 1024
DEFAULT_LIST_INTERVAL = 10

TAG_MSG = 'MSG'
TAG_ERR = 'ERR'
TAG_CFG = 'CFG'
TAG_CMD = 'CMD'
TAG_LIST = 'LIST'
TAG_FILE = 'FILE'


class ClientEventEmitter(EventEmitter):
    def __init__(self, client):
        EventEmitter.__init__(self)

        self.client = client

    def run(self):
        while True:
            received_message = self.client.receive_from_socket()
            tag, received_message = self.client.parse_received_message(received_message)

            if tag == TAG_MSG:
                author, message = self.client.parse_received_message(received_message, ';')

                self.emit('message', [author, message])
                continue
            if tag == TAG_ERR:
                self.emit('error', [received_message])
                continue
            if tag == TAG_CFG:
                self.emit('config', [received_message])
                continue
            if tag == TAG_CMD:
                if received_message.startswith('connect'):
                    peer_username = received_message[len('connect '):]
                    self.emit('connect', [peer_username])

                elif received_message.startswith('disconnect'):
                    peer_username = received_message[len('disconnect '):]
                    self.emit('disconnect', [peer_username])

                self.emit('command', [received_message])
                continue
            if tag == TAG_LIST:
                self.emit('list', [received_message])
            if tag == TAG_FILE:
                self.emit('file', [received_message])


class Client:
    def __init__(self, host: str, chat_port: int, file_transfer_port: int, username: str, **kwargs):
        self.emitter = ClientEventEmitter(self)
        self.list_executor = IntervalExecutor(kwargs.get('list_interval') or DEFAULT_LIST_INTERVAL, self.request_list)

        self.host = host
        self.chat_port = chat_port
        self.file_transfer_port = file_transfer_port
        self.username = username

        self.socket = None
        self.buf_size = kwargs.get('buffer_size') or DEFAULT_BUFFER_SIZE

        self.file_transfer_uploader = None
        self.file_transfer_downloader = None

        self.on_file_downloaded = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.chat_port))

        self._set_username()

        self._register_events()
        self.emitter.start()
        self.list_executor.start()

    def connect_to_user(self, username: str):
        return self.send_to_socket(TAG_CMD, f'connect {username}')

    def disconnect_from_user(self, username: str):
        return self.send_to_socket(TAG_CMD, f'disconnect {username}')

    def send_exit(self):
        return self.send_to_socket(TAG_CMD, 'exit')

    def send_message_to(self, recipient: str, message: str):
        return self.send_to_socket(TAG_MSG, f'{recipient};{message}')

    def request_list(self):
        return self.send_to_socket(TAG_CMD, 'list')

    def send_file(self, destination_user: str, filename: str, file_path: str):
        self.file_transfer_uploader = FileTransferUploader(self.username, destination_user, self.host, self.file_transfer_port, buffer_size=self.buf_size)
        self.file_transfer_uploader.set_file_data(filename, file_path)
        self.file_transfer_uploader.start()

    def set_on_file_downloaded(self, on_file_downloaded):
        self.on_file_downloaded = on_file_downloaded

    def _set_username(self):
        self.send_to_socket(TAG_CFG, f'set_username {self.username}')
        username_response = self.receive_from_socket()
        tag, username_response = self.parse_received_message(username_response)

        if tag == TAG_ERR:
            print(username_response)
            self.socket.close()
            sys.exit(1)

    def _register_events(self):
        self.emitter.on('message', self._handle_message)
        self.emitter.on('error', self._handle_error)
        self.emitter.on('config', self._handle_config)
        self.emitter.on('command', self._handle_command)
        self.emitter.on('list', self._handle_list)
        self.emitter.on('file', self._handle_file)

    @staticmethod
    def _handle_message(author: str, message: str):
        print(f'[SERVER]: {author} said: {message}')

    @staticmethod
    def _handle_error(error: str):
        print(f'[SERVER]: Oops! Something happened: {error}')

    @staticmethod
    def _handle_config(config: str):
        print(f'[SERVER]: Received config result: {config}')

    @staticmethod
    def _handle_command(command: str):
        print(f'[SERVER]: Received command from server: {command}')

    @staticmethod
    def _handle_list(user_list: str):
        print(f'[SERVER]: Users online: {user_list}')

    def _handle_file(self, file_header: str):
        header_split = file_header.split(';')

        source_user = header_split[0]
        filename = header_split[1]
        file_size = int(header_split[2])

        print(f'[SERVER]: User {source_user} has sent the file {filename}')
        self.file_transfer_downloader = FileTransferDownloader(filename, file_size, self.host, self.file_transfer_port, buffer_size=self.buf_size)
        self.file_transfer_downloader.set_on_finished(self.on_file_downloaded)
        self.file_transfer_downloader.start()

    def receive_from_socket(self) -> str:
        if self.socket is None:
            raise Exception('No socket connection is available to this client.')

        data = self.socket.recv(self.buf_size)

        if not data:
            raise Exception('No data received on socket. Was the connection interrupted?')

        return data.decode('ASCII')

    def send_to_socket(self, tag: str, message: str):
        if self.socket is None:
            raise Exception('No socket connection is available to this client.')

        self.socket.sendall(f'{tag}|{message}'.encode('ASCII'))

    @staticmethod
    def parse_received_message(received_message: str, separator='|'):
        separator_index = received_message.index(separator)

        tag = received_message[:separator_index]
        received_message = received_message[separator_index + 1:]

        return tag, received_message
