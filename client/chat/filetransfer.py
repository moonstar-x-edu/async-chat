import socket
import os
from pathlib import Path
from threading import Thread

DEFAULT_BUFFER_SIZE = 1024

DOWNLOADS_FOLDER = os.path.abspath(f'{Path.home()}/Downloads')


class FileTransferUploader(Thread):
    def __init__(self, source_user: str, destination_user: str, host: str, port: int, **kwargs):
        Thread.__init__(self)
        self.daemon = True

        self.source_user = source_user
        self.destination_user = destination_user
        self.host = host
        self.port = port

        self.filename = ''
        self.file_path = ''

        self.socket = None
        self.buf_size = kwargs.get('buffer_size') or DEFAULT_BUFFER_SIZE

    def run(self):
        self.connect()
        file_size = os.path.getsize(self.file_path)

        self.send_upload_header(file_size)

        uploaded = 0

        with open(self.file_path, 'rb') as file:
            while True:
                part_content = file.read(self.buf_size)

                if len(part_content) == 0:
                    break

                self.send_part(part_content)

                uploaded += self.buf_size
                print(f'[FILETRANSFER UPLOADER]: Transferred {int(100 * uploaded / file_size)}%')

        print(f'[FILETRANSFER UPLOADER]: File transfer completed, disconnecting...')
        self.disconnect()

    def set_file_data(self, filename: str, file_path: str):
        self.filename = filename
        self.file_path = file_path

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        print(f'[FILETRANSFER UPLOADER]: Connected to file transfer server at {self.host}:{self.port}')

    def disconnect(self):
        self.socket.close()
        self.socket = None

        print('[FILETRANSFER UPLOADER]: Disconnected from file transfer server.')

    def send_upload_header(self, file_size: int):
        header = f'UP;{self.source_user};{self.destination_user};{self.filename};{file_size}'
        self.send_message(header)
        print(f'[FILETRANSFER UPLOADER]: Sent upload header: {header}')

        response = self.receive_message()

        if response == 'ERROR':
            raise Exception('The server refused to receive a file.')

        print(f'[FILETRANSFER UPLOADER]: Server accepted upload operation. Uploading...')

    def send_part(self, part_content: bytes):
        if self.socket is None:
            raise Exception('No socket connection is available to this file uploader.')

        self.socket.sendall(part_content)

    def send_message(self, message: str):
        if self.socket is None:
            raise Exception('No socket connection is available to this file uploader.')

        self.socket.sendall(message.encode('ASCII'))

    def receive_message(self) -> str:
        if self.socket is None:
            raise Exception('No socket connection is available to this file uploader.')

        data = self.socket.recv(self.buf_size)

        if not data:
            raise Exception('No data received on socket. Was the connection interrupted?')

        return data.decode('ASCII')


class FileTransferDownloader(Thread):
    def __init__(self, filename: str, file_size: int, host: str, port: int, **kwargs):
        Thread.__init__(self)
        self.daemon = True

        self.filename = filename
        self.file_size = file_size

        self.host = host
        self.port = port

        self.socket = None
        self.buf_size = kwargs.get('buffer_size') or DEFAULT_BUFFER_SIZE

        self.on_finished = None

    def run(self):
        self.connect()
        self.send_download_header()

        file_path = os.path.abspath(f'{DOWNLOADS_FOLDER}/{self.filename}')
        downloaded = 0

        with open(file_path, 'wb') as file:
            while True:
                received_part = self.receive_part()

                if received_part is None or len(received_part) == 0:
                    break

                file.write(received_part)

                downloaded += self.buf_size
                print(f'[FILETRANSFER DOWNLOADER]: Downloaded {int(100 * downloaded / self.file_size)}%')

        print(f'[FILETRANSFER DOWNLOADER]: File available at: {file_path}')
        print(f'[FILETRANSFER DOWNLOADER]: Download finished. Disconnecting...')

        self.disconnect()

        if self.on_finished is not None:
            self.on_finished(file_path)

    def set_on_finished(self, on_finished):
        self.on_finished = on_finished

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        print(f'[FILETRANSFER DOWNLOADER]: Connected to file transfer server at {self.host}:{self.port}')

    def disconnect(self):
        self.socket.close()
        self.socket = None

        print('[FILETRANSFER DOWNLOADER]: Disconnected from file transfer server.')

    def send_download_header(self):
        header = f'DOWN;;;{self.filename};'
        self.send_message(header)
        print(f'[FILETRANSFER DOWNLOADER]: Sent download header: {header}')

        response = self.receive_message()

        if response == 'ERROR':
            raise Exception('The server refused to send a file.')

        print(f'[FILETRANSFER DOWNLOADER]: Server accepted download operation. Downloading...')

    def receive_part(self) -> bytes:
        if self.socket is None:
            raise Exception('No socket connection is available to this file downloader.')

        return self.socket.recv(self.buf_size)

    def send_message(self, message: str):
        if self.socket is None:
            raise Exception('No socket connection is available to this file uploader.')

        self.socket.sendall(message.encode('ASCII'))

    def receive_message(self) -> str:
        if self.socket is None:
            raise Exception('No socket connection is available to this file uploader.')

        data = self.socket.recv(self.buf_size)

        if not data:
            raise Exception('No data received on socket. Was the connection interrupted?')

        return data.decode('ASCII')
