from enum import Enum
from shared.protobuf import Action, ResponseCode


# This must match the protobuf structure
class Action(Enum):
    LOGIN = Action.LOGIN
    LOGOUT = Action.LOGOUT
    CONNECT = Action.CONNECT
    DISCONNECT = Action.DISCONNECT
    SEARCH = Action.SEARCH
    MESSAGE = Action.MESSAGE


class ResponseCode(Enum):
    SUCCESS = ResponseCode.SUCCESS
    ERROR = ResponseCode.ERROR


class State(Enum):
    CHATTING = 1
    CONNECTED = 2
    OFFLINE = 3


class Commands(Enum):
    CONNECT_TO_PEER = 1
    SEARCH_FOR_MESSAGE = 2
    DISCONNECT_FROM_PEER = 3
