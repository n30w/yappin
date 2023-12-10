"""
Physical application that is the client.
"""

from shared.protobuf import Action, serialize
from shared.message import DataMessage
from shared.net import *
from shared import *

A_LOGIN = 0
A_LOGOUT = 1
A_CONNECT = 2
A_DISCONNECT = 3
A_SEARCH = 4
A_MESSAGE = 5


class Client:
    def __init__(self, config: Config, username: str) -> None:
        self.socket = Socket(config)
        self.__config = config
        self.__username = username

    def run(self):
        make_message = from_sender(self.__username)
        msg = make_message("hello there everyone", A_MESSAGE)

        self.socket.connect()
        self.socket.transmit(msg)
        self.socket.close()


def from_sender(sender: str):
    dm = DataMessage()
    dm.sender = sender

    def create(text: str, action: int) -> bytes:
        dm.action = action
        dm.messages.append(text.encode())
        dm.pubkey = "123456"
        return dm.SerializeToString()

    return create
