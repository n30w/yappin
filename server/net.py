import socket, select
from typing import Any, Self
from shared.net import Config, Pluggable
from shared.chat_types import *
from shared.enums import State

# Network things for server only.


class Peer(Pluggable):
    def __init__(self, config: Config) -> None:
        self.config: Config = config
        super().__init__(self.config)

        # a peer is only initialized when it is connected
        self.__state: State = State.CONNECTED

    def consume(self, message: bytes) -> None:
        """
        Consumes either a Message or an Action and does something with it.
        """
        err = self.__socket.transmit(message)
        if err is not None:
            print(err)

    def get_state(self) -> State:
        """Gets the state"""
        return self.__state

    def set_state(self, state: State) -> State:
        """Sets and returns the state it was set to"""
        self.__state = state
        return self.__state


class Server(Pluggable):
    """Class that defines the 'network' component of what a server is. The thing that calls the shots."""

    def __init__(self, config: Config) -> None:
        self.config: Config = config
        super().__init__(self.config)

    def read_connections(self, connections: list[Pluggable]) -> list[Any]:
        """
        Reads connections using select.select, returns the list of read connections.
        """

        sockets: list = []
        # turn the list of connections into sockets
        for c in connections:
            sockets.append(c.get_socket())

        # read the sockets
        read, _write, _error = select.select(sockets, [], [])
        return read
