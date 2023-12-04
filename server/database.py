"""
Defines a database that the server can use. Possible to interface with actual database like SQL.
"""


from server.peer import ChatPeer
from shared.enums import State


class Database:
    def __init__(self) -> None:
        self.__users_status: dict[str, State] = {}
        self.__internal: dict[any, any] = {}

    def store(self, k: any, v: any) -> None:
        self.__internal[k] = v

    def set_user_state(self, user: str, state: State) -> None:
        self.__users_status[user] = state

    def get_user_state(self, user: ChatPeer) -> State:
        return self.__users_status[user.username]

    def consume(self, data: T):
        pass

    def __contains__(self, item: str) -> bool:
        return item in self.__users_status.keys()
