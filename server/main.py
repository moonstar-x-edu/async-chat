import os
from chat.server import Server, DEFAULT_PORT, DEFAULT_BUFFER_SIZE, DEFAULT_MAX_CONNECTIONS


def main():
    print('Starting server...')

    options = {
        'port': int(os.getenv('PORT') or DEFAULT_PORT),
        'buffer_size': int(os.getenv('BUFFER_SIZE') or DEFAULT_BUFFER_SIZE),
        'max_connections': int(os.getenv('MAX_CONNECTIONS') or DEFAULT_MAX_CONNECTIONS)
    }

    server = Server(options.get('port'), buffer_size=options.get('buffer_size'), max_connections=options.get('max_connections'))
    server.start()
    server.listen_for_connections()


if __name__ == '__main__':
    main()
