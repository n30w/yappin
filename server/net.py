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
        self.online_connections: list[any] = []

        # translation tools
        self.socket_to_pluggable: dict[socket.socket, Pluggable] = {}
        self.pluggable_to_socket: dict[Pluggable, socket.socket] = {}

        # str is an arbitrary string identifier for the Pluggable type
        self.active_connections: dict[str, Pluggable] = {}

    def purge_links(self, connection: Pluggable) -> Pluggable:
        sock = self.pluggable_to_socket.pop(connection)
        plug = self.socket_to_pluggable.pop(sock)
        return plug

    def connections_to_sockets(
        self, connections: list[Pluggable]
    ) -> list[socket.socket]:
        sockets: list[socket.socket] = []
        for c in connections:
            sockets.append(c.get_socket())
        return sockets

    def sockets_to_connections(self, sockets: list[socket.socket]) -> list[Pluggable]:
        connections: list[Pluggable] = []
        for s in sockets:
            connections.append(self.socket_to_pluggable[s])
        return connections

    def read_connections(self, connections: list[Pluggable]) -> list[Pluggable]:
        """
        Reads connections using select.select, returns the list of read connections.
        """

        sockets: list = []

        # turn the list of connections into sockets
        for c in connections:
            sockets.append(c.get_socket())

        # read the sockets
        read, _write, _error = select.select(sockets, [], [])

        plugs: list = []

        # from the sockets, get their corresponding plugs
        for r in read:
            plugs.append(self.socket_to_pluggable[r])

        return plugs

    def link_socket_and_plug(self, sock: socket.socket, plug: Pluggable):
        """
        Links a socket and a peer together, both ways.
        """
        self.socket_to_pluggable[sock] = plug
        self.pluggable_to_socket[plug] = sock
