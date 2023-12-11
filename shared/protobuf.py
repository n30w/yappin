"""
This file creates a protobuf interface, wraps them.
"""

from enum import Enum
from shared.message import (
    DataMessage,
    DataMessageClientRequest,
    DataMessageResponseCode,
)


# This must match the protobuf structure
class Action(Enum):
    LOGIN = DataMessageClientRequest.ACTION_LOGIN
    LOGOUT = DataMessageClientRequest.ACTION_LOGOUT
    CONNECT = DataMessageClientRequest.ACTION_CONNECT
    DISCONNECT = DataMessageClientRequest.ACTION_DISCONNECT
    SEARCH = DataMessageClientRequest.ACTION_SEARCH
    MESSAGE = DataMessageClientRequest.ACTION_MESSAGE


class ResponseCode(Enum):
    SUCCESS = DataMessageResponseCode.RESPONSE_CODE_SUCCESS
    ERROR = DataMessageResponseCode.RESPONSE_CODE_ERROR


def build_server_response(res_code: ResponseCode, comment: str) -> bytes:
    """builds a message into bytes that can be sent. The bytes outputted are ALREADY SERIALIZED. The text supplied is put into the message params attribute."""
    message = DataMessage()
    message.sender = "SERVER"
    message.response.response = res_code
    message.response.comment = comment
    return serialize(message)


def deserialize(data: bytes) -> DataMessage:
    dm = DataMessage()
    return dm.parse(data)


def serialize(data: DataMessage) -> bytes:
    return data.SerializeToString()
