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
        print(f"Starting client as {self.__username}")
        make_message = from_sender(self.__username)
        self.socket.connect()
        msg = make_message("hello", A_LOGIN)
        self.socket.transmit(msg)

        try:
            while True:
                user_input = input("Enter message (/q to exit): ")
                if user_input.lower() == "/q":
                    break

                msg = make_message(user_input, A_LOGIN)
                # self.socket.transmit(msg)

        except Exception as e:
            print(f"Error: {e}")

        finally:
            self.socket.close()
            print("Connection terminated")


def from_sender(sender: str):
    dm = DataMessage()
    dm.sender = sender

    def create(text: str, action: int) -> bytes:
        dm.action = action
        dm.params = text
        dm.pubkey = "123456"
        return dm.SerializeToString()

    return create
