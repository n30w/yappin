import betterproto
from client.encryption import Key
from server.net import Config
from shared.enums import *
from server.net import *
from shared.protobuf import serialize
from shared.types import *
from shared.message import UserMessage


class Message:
    """
    Message wraps the Protobuf objects created by the Protobuf compiler.
    """

    def __init__(self) -> None:
        self.body: str = ""
        self.user_message = UserMessage

    def create(self) -> bool:
        """
        create makes a message and updates the state of the peer object accordingly.
        """
        return True


class ChatPeer(Peer):
    def __init__(self, config: Config, username: str, key: Key) -> None:
        super().__init__(config)
        self.username: str = username
        self.key: Key = key

    def consume(message: bytes):
        # Turns the message back into protobuf serialization format
        message = serialize(message)
        super().consume(message)
