import sys
from chat.client import Client
from ui.chat_interface import ChatInterface
from tkinter import *
from tkinter import ttk

def main():
    try:
        host = sys.argv[1]
    except IndexError:
        print('Please include the host to connect to: python main.py <host> <port>')
        sys.exit(1)

    try:
        port = sys.argv[2]
    except IndexError:
        print('Please include the host to connect to: python main.py <host> <port>')
        sys.exit(1)

    print('Starting client...')

    client = Client(host, int(port))
    client.connect()
    client.send_to_socket('CMD', 'HI') # Testing sending while receiving.

    # while True:
    #     pass # Keep alive (not necessary with UI)

    root = Tk()
    ChatInterface(root)
    root.mainloop()

if __name__ == '__main__':
    main()
