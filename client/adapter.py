"""
Used for adapting from this client code to GUI Tkinter code.
"""

from client.client import Client
from net import Config


class GUIClientAdapter(Client):
    def __init__(self, username: str) -> None:
        config: Config = Config(socket_blocking=False)
        super().__init__(config, username)
