import socket
from client.utils.events import EventEmitter

DEFAULT_BUFFER_SIZE = 1024


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

            if tag == 'MSG':
                return self.emit('message', [received_message])
            if tag == 'ERR':
                return self.emit('error', [received_message])
            if tag == 'INFO':
                return self.emit('info', [received_message])


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
        self.emitter.on('info', self._handle_info)

    def _handle_message(self, message: str) -> None:
        print(f'MESSAGE: {message}')

    def _handle_error(self, error: str) -> None:
        print(f'ERROR: {error}')

    def _handle_info(self, info: str) -> None:
        print(f'ANNONCEMENT: {info}')

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
