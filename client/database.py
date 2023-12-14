""" Data structures to hold chats and such """


# ChatMessage is a tuple, a username, and a list of messages from that username.
from shared.crypto import base_64_to_public_key
from shared.encryption import Key, RSAKey
from shared.message import DataMessage


type ChatMessage = tuple[str, list[str]]
type ChatLog = list[ChatMessage]
type ChatLogs = dict[str, ChatLog]


class Database:
    def __init__(self) -> None:
        # chat_logs, pertains to the chat logs between you and other person. Key is username, value is array of messages in sequential order in their sent and received order.
        self.chat_logs: ChatLogs = {}

        # Keys of senders/contacts. Used to encrypt outgoing messages.
        self.sender_keys: dict[str, RSAKey] = {}

    def store_message(self, message: DataMessage) -> None:
        """
        Stores a message in the chat log
        """

        name: str = message.sender

        if name not in self.chat_logs.keys():
            self.chat_logs[name] = []

        chat_message: ChatMessage = (name, message.messages)

        self.chat_logs[name].append(chat_message)

        return None

    def get_chat_log(self, username: str) -> ChatLog:
        return self.chat_logs.get(username)

    def store_key(self, message: DataMessage) -> None:
        """
        Stores a public key from a sender given a utf-8 string. The public key is expected to be encoded in base64.
        """

        # DIFFERENCE! message.params stores the sender name of the key, the other peer.
        name: str = message.params
        pub_key: str = message.pubkey

        # check if the key is already in the database
        if name not in self.sender_keys.keys():
            # if its not, make a new key
            key = base_64_to_public_key(pub_key)
            self.sender_keys[name] = RSAKey(key)

        return None

    def get_key(self, username: str) -> Key:
        return self.sender_keys[username]
