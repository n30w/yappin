"""
Defines a database that the server can use. Possible to interface with actual database like SQL.
"""


from shared.chat_types import T
from net import Config
from peer import ChatPeer
from shared.enums import State


class Database:
    def __init__(self) -> None:
        self.__users_status: dict[str, State] = {}
        self.__internal: dict[any, any] = {}
        self.__user_configs: dict[str, Config] = {}

    def store_config(self, user: ChatPeer):
        self.__user_configs[user.username] = user.config

    def get_config(self, username: str) -> Config:
        return self.__user_configs[username]

    def set_user_state(self, user: str, state: State) -> None:
        self.__users_status[user] = state

    def get_user_state(self, user: ChatPeer) -> State:
        return self.__users_status[user.username]

    def consume(self, data: T):
        pass

    def __contains__(self, item: str) -> bool:
        return item in self.__users_status.keys()
