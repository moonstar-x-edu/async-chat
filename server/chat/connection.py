from socket import socket
from threading import Thread


class Connection(Thread):
    def __init__(self, server, client_socket: socket, client_address: tuple):
        Thread.__init__(self)
        self.daemon = True

        self.server = server
        self.socket = client_socket
        self.address = client_address
        self.username = None

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

        if tag == 'MSG':
            return self._handle_message(received_message)
        if tag == 'CMD':
            return self._handle_command(received_message)

    def _handle_message(self, message: str) -> None:
        self._send_to_socket('MSG', message)

    def _handle_command(self, command: str) -> None:
        self._send_to_socket('ERR', command)

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
