import betterproto
from client.encryption import Key
from net import Config
from shared.enums import *
from net import *
from shared.protobuf import serialize
from shared.chat_types import *


class ChatPeer(Peer):
    def __init__(self, config: Config, username: str, key: Key) -> None:
        super().__init__(config)
        self.username: str = username
        self.key: Key = key

    def consume(message: bytes):
        # Turns the message back into protobuf serialization format
        message = serialize(message)
        super().consume(message)
