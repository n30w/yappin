from enum import Enum
from shared.protobuf import Action, ResponseCode

# Actions in int form
ACTION_LOGIN = 0
ACTION_LOGOUT = 1
ACTION_CONNECT = 2
ACTION_DISCONNECT = 3
ACTION_SEARCH = 4
ACTION_MESSAGE = 5


# This must match the protobuf structure
class Action(Enum):
    LOGIN = Action.LOGIN
    LOGOUT = Action.LOGOUT
    CONNECT = Action.CONNECT
    DISCONNECT = Action.DISCONNECT
    SEARCH = Action.SEARCH
    MESSAGE = Action.MESSAGE
    LIST = Action.LIST


ACTIONS: list[Action] = [
    Action.LOGIN,
    Action.LOGOUT,
    Action.CONNECT,
    Action.DISCONNECT,
    Action.SEARCH,
    Action.MESSAGE,
    Action.LIST,
]


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
