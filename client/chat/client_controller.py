from .client import Client, TAG_MSG, TAG_CMD, TAG_ERR, TAG_LIST, TAG_CFG


class ClientController:
    def __init__(self, client: Client):
        self.client = client

