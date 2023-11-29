from server.net import *
from shared.types import *


class Key:
    """
    Key represents the private or public that each peer posses. The "key" itself is just a long string of numbers and letters.

    ---

    ### Methods
        get() -- returns the key
        set(value: str) -- sets the key
    """

    def __init__(self, value: str = "") -> None:
        self.__value: str = value

    def get(self) -> str:
        return self.__value

    def set(self, value: str):
        self.__value = value


class Message:
    """
    Message wraps the Protobuf objects created by the Protobuf compiler.
    """

    def __init__(self) -> None:
        self.body: str = ""

    def create(self) -> bool:
        """
        create makes a message and updates the state of the peer object accordingly.
        """
        return True


class Action:
    pass


class Peer:
    def __init__(self, config: Config, key: Key) -> None:
        self.config: Config = config
        self.__key: Key = key
        self.__socket: Socket = Socket(self.config)

    def get_key(self) -> str:
        return self.__key.get()

    def consume(self, obj: Message | Action) -> None:
        """
        Consumes either a Message or an Action and does something with it.
        """
        pass
