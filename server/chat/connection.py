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

    def is_engaged(self) -> bool:
        return self.peer is not None

    def send_to_peer(self, message: str) -> None:
        if self.peer is None:
            return self.send_to_socket(TAG_ERR, 'No peer to send a message to.')

        return self.peer.send_to_socket(TAG_MSG, message)

    def connect_to(self, peer_connection) -> None:
        if peer_connection == self:
            return self.send_to_socket(TAG_ERR, 'You cannot chat with yourself.')

        self.peer = peer_connection
        peer_connection.peer = self
        self.peer.send_to_socket(TAG_CMD, f'connect {self.username}')

        self.log('INFO', f'Chatting now with {peer_connection.address}')
        return self.send_to_socket(TAG_CMD, 'SUCCESS')

    def disconnect_from_peer(self) -> None:
        if not self.is_engaged():
            return self.send_to_socket(TAG_ERR, 'You are not chatting with anyone currently.')

        self.peer.send_to_socket(TAG_CMD, 'disconnect')
        self.log('INFO', f'No longer chatting with {self.peer.address}')

        self.peer.peer = None
        self.peer = None
        return self.send_to_socket(TAG_CMD, 'SUCCESS')

    def run(self) -> None:
        try:
            while True:
                self.handle_received_message(self.receive_from_socket())

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

        return self.send_to_socket(TAG_ERR, 'Message sent with an invalid tag.')

    def _handle_message(self, message: str) -> None:
        if not self.is_engaged():
            return self.send_to_socket(TAG_ERR, 'You are not connected to anybody else.')

        return self.send_to_peer(message)

    def _handle_command(self, command: str) -> None:
        if command == 'list':
            return self.send_to_socket(TAG_LIST, self.server.get_online_list())

        if command.startswith('connect'):
            peer_username = command[len('connect '):]
            peer_connection = self.server.get_connection_by_username(peer_username)
            if peer_connection is None:
                return self.send_to_socket(TAG_ERR, 'Username not found.')

            return self.connect_to(peer_connection)

        if command == 'disconnect':
            if self.is_engaged():
                return self.disconnect_from_peer()

            self.send_to_socket(TAG_CMD, 'exit')
            return self.server.close_connection(self)

        return self.send_to_socket(TAG_ERR, 'Invalid CMD message sent.')

    def _handle_config(self, config: str) -> None:
        if config.startswith('set_username'):
            username = config[len('set_username '):]

            if self.server.get_connection_by_username(username) is not None:
                return self.send_to_socket(TAG_ERR, 'Username already in use.')

            self.username = username
            self.log('INFO', f'Saved username for client as {self.username}')
            return self.send_to_socket(TAG_CFG, 'SUCCESS')

        return self.send_to_socket(TAG_ERR, 'Invalid CFG message sent.')

    def receive_from_socket(self) -> str:
        if self.socket is None:
            raise Exception('No socket connection is available to this client.')

        data = self.socket.recv(self.server.buf_size)

        if not data:
            raise Exception('No data received on socket. Was the connection interrupted?')

        data = data.decode('ASCII')
        self.log('DEBUG', f'Received message: {data}')

        return data

    def send_to_socket(self, tag: str, message: str) -> None:
        if self.socket is None:
            raise Exception('No socket connection is available to this client.')

        to_send = f'{tag}|{message}'
        self.log('DEBUG', f'Sending message: {to_send}')

        self.socket.sendall(to_send.encode('ASCII'))

    def log(self, label: str, message: str) -> None:
        print(f'({self.address}): [{label}] - {message}')
