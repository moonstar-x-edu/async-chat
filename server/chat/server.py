import socket
from typing import Optional
from .connection import Connection

DEFAULT_PORT = 10023
DEFAULT_BUFFER_SIZE = 1024
DEFAULT_MAX_CONNECTIONS = 100


class Server:
    def __init__(self, port: int, **kwargs):
        self.port = port
        self.buf_size = kwargs.get('buffer_size') or DEFAULT_BUFFER_SIZE
        self.max_connections = kwargs.get('max_connections') or DEFAULT_MAX_CONNECTIONS

        self.connections = dict()
        self.socket = None

    def start(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', self.port))
        self.socket.listen(self.max_connections)

        self.log('INFO', f'Server started on port {self.port}')

    def listen_for_connections(self) -> None:
        if self.socket is None:
            raise Exception('No socket connection is available to this server.')

        while True:
            try:
                client_socket, client_address = self.socket.accept()

                connection = Connection(self, client_socket, client_address)
                self.connections[client_address] = connection
                connection.log('INFO', 'Received connection.')
                connection.start()

            except Exception or KeyboardInterrupt:
                break

        self.log('INFO', 'Closing server...')
        self.close_server()

    def get_connections(self) -> list:
        return list(self.connections.values())

    def get_connection_by_username(self, username: str) -> Optional[Connection]:
        for connection in self.connections.values():
            if connection.username == username:
                return connection

        return None

    def get_online_list(self):
        connections = filter(lambda c: c.is_engaged(), self.connections.values())
        user_list = map(lambda c: c.username, connections)
        user_list = filter(lambda u: u is not None, user_list)
        user_list = ', '.join(user_list)

        return user_list

    def close_connection(self, connection: Connection) -> None:
        if self.connections.get(connection.address) is None:
            return

        connection.socket.close()
        connection.log('INFO', 'Closed connection.')

        del self.connections[connection.address]

    def close_server(self) -> None:
        if self.socket is None:
            raise Exception('No socket connection is available to this server.')

        self.socket.close()
        for connection in self.connections.values():
            connection.socket.close()

    @staticmethod
    def log(label: str, message: str) -> None:
        print(f'(SERVER): [{label}] - {message}')
