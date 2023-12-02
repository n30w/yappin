# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: message.proto
# plugin: python-betterproto
from dataclasses import dataclass
from typing import List

import betterproto


class DataMessageClientRequest(betterproto.Enum):
    ACTION_LOGIN = 0
    ACTION_LOGOUT = 1
    ACTION_CONNECT = 2
    ACTION_DISCONNECT = 3
    ACTION_SEARCH = 4
    ACTION_MESSAGE = 5


class DataMessageResponseCode(betterproto.Enum):
    RESPONSE_CODE_SUCCESS = 0
    RESPONSE_CODE_ERROR = 1


@dataclass
class DataMessage(betterproto.Message):
    action: "DataMessageClientRequest" = betterproto.enum_field(1)
    response: "DataMessageServerResponse" = betterproto.message_field(2)
    messages: List["DataMessageChatMessage"] = betterproto.message_field(3)
    sender: str = betterproto.string_field(4)
    pubkey: str = betterproto.string_field(5)
    params: str = betterproto.string_field(6)


@dataclass
class DataMessageServerResponse(betterproto.Message):
    """Response from the server with an accompanying message."""

    response: "DataMessageResponseCode" = betterproto.enum_field(1)
    comment: str = betterproto.string_field(2)


@dataclass
class DataMessageChatMessage(betterproto.Message):
    """A message in chat"""

    sender: str = betterproto.string_field(1)
    receiver: str = betterproto.string_field(2)
    body: str = betterproto.string_field(3)
    date: str = betterproto.string_field(4)
