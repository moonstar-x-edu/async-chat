class CLIClient:
    def __init__(self, client):
        self.client = client

    def start(self):
        try:
            while True:
                message = input('> ')
                message = message.split('|')
                tag = message[0]
                message = message[1]
                self.client.send_to_socket(tag, message)
        except IndexError:
            self.start()
        except KeyboardInterrupt:
            print('Exiting client...')
