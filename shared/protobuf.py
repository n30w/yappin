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


def deserialize(data: str) -> DataMessage:
    return DataMessage.ParseFromString(data)


def serialize(data: DataMessage) -> str:
    return data.SerializeToString()
