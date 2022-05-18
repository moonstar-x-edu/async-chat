import sys
from chat.client import Client
from ui.chat_interface import ChatInterface
from tkinter import *


def main():
    try:
        host = sys.argv[1]
    except IndexError:
        print('Please include the host to connect to: python main.py <host> <chat_port> <file_transfer_port> <username>')
        sys.exit(1)

    try:
        chat_port = sys.argv[2]
    except IndexError:
        print('Please include the chat port to connect to: python main.py <host> <chat_port> <file_transfer_port> <username>')
        sys.exit(1)

    try:
        file_transfer_port = sys.argv[3]
    except IndexError:
        print('Please include the file transfer port to connect to: python main.py <host> <chat_port> <file_transfer_port> <username>')
        sys.exit(1)

    try:
        username = sys.argv[4]
    except IndexError:
        print('Please include your username: python main.py <host> <chat_port> <file_transfer_port> <username>')
        sys.exit(1)

    print('Starting client...')

    client = Client(host, int(chat_port), int(file_transfer_port), username)
    client.connect()

    root = Tk()
    ChatInterface(root, client)
    root.mainloop()


if __name__ == '__main__':
    main()
