import betterproto
from shared.net import Config
from server.net import Peer
from shared.encryption import Key
from shared.enums import *
from shared.protobuf import serialize
from shared.chat_types import *


class ChatPeer(Peer):
    def __init__(self, config: Config, username: str, key: str) -> None:
        super().__init__(config)
        self.username: str = username
        self.Key: str = key

    def consume(message: bytes):
        # Turns the message back into protobuf serialization format
        message = serialize(message)
        super().consume(message)
