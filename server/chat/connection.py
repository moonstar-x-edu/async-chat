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

        self.peers = dict()

    def send_to_peer(self, peer_username: str, message: str):
        peer = self.peers.get(peer_username)

        if peer is None:
            return self.send_to_socket(TAG_ERR, f'You are not chatting with {peer_username}.')

        return peer.send_to_socket(TAG_MSG, f'{self.username};{message}')

    def connect_to(self, peer_connection):
        if peer_connection == self:
            return self.send_to_socket(TAG_ERR, 'You cannot chat with yourself.')

        self.peers[peer_connection.username] = peer_connection
        peer_connection.peers[self.username] = self
        peer_connection.send_to_socket(TAG_CMD, f'connect {self.username}')

        self.log('INFO', f'Chatting now with {peer_connection.address}')
        peer_connection.log('INFO', f'Chatting now with {self.address}')

        return self.send_to_socket(TAG_CMD, 'SUCCESS')

    def disconnect_from_peer(self, peer_username: str):
        peer = self.peers.get(peer_username)

        if peer is None:
            return self.send_to_socket(TAG_ERR, f'You are not chatting with {peer_username}.')

        peer.send_to_socket(TAG_CMD, f'disconnect {self.username}')
        self.log('INFO', f'No longer chatting with {peer.address}')
        peer.log('INFO', f'No longer chatting with {self.address}')

        del self.peers[peer_username]
        del peer.peers[self.username]

        return self.send_to_socket(TAG_CMD, 'SUCCESS')

    def run(self):
        try:
            while True:
                self.handle_received_message(self.receive_from_socket())

        except BaseException as error:
            self.log('ERROR', str(error))
            self.server.close_connection(self)

    def handle_received_message(self, received_message: str):
        try:
            separator_index = received_message.index('|')
        except ValueError:
            return self.send_to_socket(TAG_ERR, 'Badly constructed message.')

        tag = received_message[:separator_index]
        received_message = received_message[separator_index + 1:]

        if tag == TAG_MSG:
            return self._handle_message(received_message)
        if tag == TAG_CMD:
            return self._handle_command(received_message)
        if tag == TAG_CFG:
            return self._handle_config(received_message)

        return self.send_to_socket(TAG_ERR, 'Message sent with an invalid tag.')

    def _handle_message(self, message: str):
        try:
            separator_index = message.index(';')
        except ValueError:
            return self.send_to_socket(TAG_ERR, 'Badly constructed message.')

        peer_username = message[:separator_index]
        message_content = message[separator_index + 1:]

        return self.send_to_peer(peer_username, message_content)

    def _handle_command(self, command: str):
        if command == 'list':
            return self.send_to_socket(TAG_LIST, self.server.get_online_list())

        if command.startswith('connect'):
            peer_username = command[len('connect '):]

            if len(peer_username) < 1:
                return self.send_to_socket(TAG_ERR, 'You need to specify a user to connect to.')

            peer_connection = self.server.get_connection_by_username(peer_username)
            if peer_connection is None:
                return self.send_to_socket(TAG_ERR, 'Username not found.')

            return self.connect_to(peer_connection)

        if command.startswith('disconnect'):
            peer_username = command[len('disconnect '):]

            if len(peer_username) < 1:
                return self.send_to_socket(TAG_ERR, 'You need to specify a user to connect to.')

            return self.disconnect_from_peer(peer_username)

        if command == 'exit':
            for peer_username in self.peers.keys():
                self.disconnect_from_peer(peer_username)

            return self.server.close_connection(self)

        return self.send_to_socket(TAG_ERR, 'Invalid CMD message sent.')

    def _handle_config(self, config: str):
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

    def send_to_socket(self, tag: str, message: str):
        if self.socket is None:
            raise Exception('No socket connection is available to this client.')

        to_send = f'{tag}|{message}'
        self.log('DEBUG', f'Sending message: {to_send}')

        self.socket.sendall(to_send.encode('ASCII'))

    def log(self, label: str, message: str):
        print(f'({self.address}): [{label}] - {message}')
