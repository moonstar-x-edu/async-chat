import socket
from client.utils.events import EventEmitter

DEFAULT_BUFFER_SIZE = 1024

TAG_MSG = 'MSG'
TAG_ERR = 'ERR'
TAG_CFG = 'CFG'
TAG_CMD = 'CMD'
TAG_LIST = 'LIST'


class ClientEventEmitter(EventEmitter):
    def __init__(self, client):
        EventEmitter.__init__(self)

        self.client = client

    def run(self) -> None:
        while True:
            received_message = self.client.receive_from_socket()
            separator_index = received_message.index('|')

            tag = received_message[:separator_index]
            received_message = received_message[separator_index + 1:]

            if tag == TAG_MSG:
                self.emit('message', [received_message])
                continue
            if tag == TAG_ERR:
                self.emit('error', [received_message])
                continue
            if tag == TAG_CFG:
                self.emit('config', [received_message])
                continue
            if tag == TAG_CMD:
                self.emit('command', [received_message])
                continue
            if tag == TAG_LIST:
                self.emit('list', [received_message])


class Client:
    def __init__(self, host: str, port: int, **kwargs):
        self.emitter = ClientEventEmitter(self)

        self.host = host
        self.port = port
        self.username = None

        self.socket = None
        self.buf_size = kwargs.get('buffer_size') or DEFAULT_BUFFER_SIZE

    def connect(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        self._register_events()
        self.emitter.start()

    def _register_events(self):
        self.emitter.on('message', self._handle_message)
        self.emitter.on('error', self._handle_error)
        self.emitter.on('config', self._handle_config)
        self.emitter.on('command', self._handle_command)
        self.emitter.on('list', self._handle_list)

    def _handle_message(self, message: str) -> None:
        print(f'Response -> MESSAGE: {message}')

    def _handle_error(self, error: str) -> None:
        print(f'Response -> ERROR: {error}')

    def _handle_config(self, config: str) -> None:
        print(f'Response -> CONFIG: {config}')

    def _handle_command(self, command: str) -> None:
        print(f'Response -> COMMAND: {command}')

    def _handle_list(self, user_list: str) -> None:
        print(f'Response -> LIST: {user_list}')

    def receive_from_socket(self) -> str:
        if self.socket is None:
            raise Exception('No socket connection is available to this client.')

        data = self.socket.recv(self.buf_size)

        if not data:
            raise Exception('No data received on socket. Was the connection interrupted?')

        return data.decode('ASCII')

    def send_to_socket(self, tag: str, message: str) -> None:
        if self.socket is None:
            raise Exception('No socket connection is available to this client.')

        self.socket.sendall(f'{tag}|{message}'.encode('ASCII'))
