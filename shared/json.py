"""JSON DataMessage implementation of Protobuf file"""
import json
from typing import List, Union, Optional
from enum import Enum


class ClientRequest(Enum):
    ACTION_LOGIN = 0
    ACTION_LOGOUT = 1
    ACTION_CONNECT = 2
    ACTION_DISCONNECT = 3
    ACTION_SEARCH = 4
    ACTION_MESSAGE = 5


class ResponseCode(Enum):
    RESPONSE_CODE_SUCCESS = 0
    RESPONSE_CODE_ERROR = 1


class ServerResponse:
    def __init__(self, response: ResponseCode, comment: str):
        self.response = response
        self.comment = comment

    def to_json(self) -> str:
        return json.dumps({"response": self.response.value, "comment": self.comment})

    @staticmethod
    def from_json(json_str: str) -> "ServerResponse":
        data = json.loads(json_str)
        return ServerResponse(ResponseCode(data["response"]), data["comment"])


class ChatMessage:
    def __init__(self, sender: str, receiver: str, body: str, date: str):
        self.sender = sender
        self.receiver = receiver
        self.body = body
        self.date = date

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(json_str: str) -> "ChatMessage":
        data = json.loads(json_str)
        return ChatMessage(**data)


class DataMessage:
    def __init__(
        self,
        action: Optional[ClientRequest],
        response: Optional[ServerResponse],
        messages: Optional[List[ChatMessage]],
        sender: str,
        pubkey: str,
        params: str,
    ):
        self.action = action
        self.response = response
        self.messages = messages if messages else []
        self.sender = sender
        self.pubkey = pubkey
        self.params = params

    def to_json(self) -> str:
        data = {
            "action": self.action.value if self.action else None,
            "response": json.loads(self.response.to_json()) if self.response else None,
            "messages": [json.loads(msg.to_json()) for msg in self.messages],
            "sender": self.sender,
            "pubkey": self.pubkey,
            "params": self.params,
        }
        return json.dumps(data)

    @staticmethod
    def from_json(json_str: str) -> "DataMessage":
        data = json.loads(json_str)
        action = ClientRequest(data["action"]) if data["action"] is not None else None
        response = (
            ServerResponse.from_json(json.dumps(data["response"]))
            if data["response"]
            else None
        )
        messages = [ChatMessage.from_json(json.dumps(msg)) for msg in data["messages"]]
        return DataMessage(
            action, response, messages, data["sender"], data["pubkey"], data["params"]
        )

    def to_bytes(self) -> bytes:
        return self.to_json().encode()

    @staticmethod
    def from_bytes(byte_data: bytes) -> "DataMessage":
        return DataMessage.from_json(byte_data.decode())


# Example usage
dm = DataMessage(
    action=ClientRequest.ACTION_LOGIN,
    response=None,
    messages=[],
    sender="user1",
    pubkey="pubkey123",
    params="",
)
json_data = dm.to_json()
print(json_data)

# To deserialize
dm_loaded = DataMessage.from_json(json_data)
print(dm_loaded.action)
