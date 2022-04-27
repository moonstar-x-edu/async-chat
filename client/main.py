import sys
from chat.client import Client
from chat.cli_client import CLIClient


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

    # Testing purposes...
    cli_client = CLIClient(client)
    cli_client.start()


if __name__ == '__main__':
    main()
