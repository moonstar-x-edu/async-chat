from socket import socket
from threading import Thread

TAG_MSG = 'MSG'
TAG_ERR = 'ERR'
TAG_CFG = 'CFG'
TAG_CMD = 'CMD'
TAG_LIST = 'LIST'


class Connection(Thread):
    def __init__(self, server, client_socket: socket, client_address: tuple):
        Thread.__init__(self)
        self.daemon = True

        self.server = server
        self.socket = client_socket
        self.address = client_address
        self.username = None

        self.peer = None

    def is_engaged(self):
        return self.peer is not None

    def run(self) -> None:
        try:
            while True:
                self.handle_received_message(self._receive_from_socket())

        except BaseException as error:
            self.log('ERROR', str(error))
            self.server.close_connection(self)

    def handle_received_message(self, received_message: str) -> None:
        separator_index = received_message.index('|')

        tag = received_message[:separator_index]
        received_message = received_message[separator_index + 1:]

        if tag == TAG_MSG:
            return self._handle_message(received_message)
        if tag == TAG_CMD:
            return self._handle_command(received_message)
        if tag == TAG_CFG:
            return self._handle_config(received_message)

    def _handle_message(self, message: str) -> None:
        if not self.is_engaged():
            return self._send_to_socket(TAG_ERR, 'You are not connected to anybody else.')

        # Send message to recipient.

    def _handle_command(self, command: str) -> None:
        if command == 'list':
            return self._send_to_socket(TAG_LIST, self.server.get_online_list())

        if command.startswith('connect'):
            # Handle client connection.
            return self._send_to_socket(TAG_CMD, 'SUCCESS')

        if command == 'disconnect':
            # Handle client disconnection.
            return self._send_to_socket(TAG_CMD, 'SUCCESS')

        return self._send_to_socket(TAG_ERR, 'Invalid CMD message sent.')

    def _handle_config(self, config: str) -> None:
        if config.startswith('set_username'):
            username = config[:config.index('set_username')]

            if self.server.get_connection_by_username(username) is not None:
                return self._send_to_socket(TAG_ERR, 'Username already in use.')

            self.username = username
            self.log('INFO', f'Saved username for client as {self.username}')
            return self._send_to_socket(TAG_CFG, 'SUCCESS')

        return self._send_to_socket(TAG_ERR, 'Invalid CFG message sent.')

    def _receive_from_socket(self) -> str:
        if self.socket is None:
            raise Exception('No socket connection is available to this client.')

        data = self.socket.recv(self.server.buf_size)

        if not data:
            raise Exception('No data received on socket. Was the connection interrupted?')

        data = data.decode('ASCII')
        self.log('DEBUG', f'Received message: {data}')

        return data

    def _send_to_socket(self, tag: str, message: str) -> None:
        if self.socket is None:
            raise Exception('No socket connection is available to this client.')

        to_send = f'{tag}|{message}'
        self.log('DEBUG', f'Sending message: {to_send}')

        self.socket.sendall(to_send.encode('ASCII'))

    def log(self, label: str, message: str) -> None:
        print(f'({self.address}): [{label}] - {message}')
