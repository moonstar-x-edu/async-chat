import sys
from chat.client import Client
from ui.chat_interface import ChatInterface
from tkinter import *
from tkinter import ttk

def main():
    try:
        host = sys.argv[1]
    except IndexError:
        print('Please include the host to connect to: python main.py <host> <port> <username>')
        sys.exit(1)

    try:
        port = sys.argv[2]
    except IndexError:
        print('Please include the port to connect to: python main.py <host> <port> <username>')
        sys.exit(1)

    try:
        username = sys.argv[3]
    except IndexError:
        print('Please include your username: python main.py <host> <port> <username>')
        sys.exit(1)

    print('Starting client...')

    client = Client(host, int(port), username)
    client.connect()

    # while True:
    #     pass # Keep alive (not necessary with UI)

    root = Tk()
    ChatInterface(root, client)
    root.mainloop()

if __name__ == '__main__':
    main()
