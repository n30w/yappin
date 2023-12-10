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


def build_message(res_code: ResponseCode, text: str) -> bytes:
    """builds a message into bytes that can be sent. The bytes outputted are ALREADY SERIALIZED"""
    message = DataMessage()
    message.response = res_code
    message.params = text
    return serialize(message)


def deserialize(data: bytes) -> DataMessage:
    return DataMessage.ParseFromString(data)


def serialize(data: DataMessage) -> bytes:
    return data.SerializeToString()
