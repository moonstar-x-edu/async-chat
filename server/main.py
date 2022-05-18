import os
from chat.chatserver import ChatServer, DEFAULT_CHAT_PORT, DEFAULT_BUFFER_SIZE, DEFAULT_MAX_CONNECTIONS
from chat.filetransfer import FileTransferServer, DEFAULT_FILE_TRANSFER_PORT


def main():
    print('Starting server...')

    options = {
        'chat_port': int(os.getenv('CHAT_PORT') or DEFAULT_CHAT_PORT),
        'file_transfer_port': int(os.getenv('FILE_TRANSFER_PORT') or DEFAULT_FILE_TRANSFER_PORT),
        'buffer_size': int(os.getenv('BUFFER_SIZE') or DEFAULT_BUFFER_SIZE),
        'max_connections': int(os.getenv('MAX_CONNECTIONS') or DEFAULT_MAX_CONNECTIONS)
    }

    server = ChatServer(options.get('chat_port'), buffer_size=options.get('buffer_size'), max_connections=options.get('max_connections'))
    file_transfer_server = FileTransferServer(server, options.get('file_transfer_port'), buffer_size=options.get('buffer_size'), max_connections=options.get('max_connections'))

    file_transfer_server.initialize()
    file_transfer_server.start()

    server.initialize()
    server.listen_for_connections()


if __name__ == '__main__':
    main()
