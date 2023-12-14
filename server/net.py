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
    """
    Server inherits from Pluggable. It its own socket and can interface with other devices on a network using TCP/UDP. A server has its own ephemeral list of connected peers, and also maintains two dictionaries, socket_to_pluggable and pluggable_to_socket, that keep track of which socket is assigned to which peer and vice versa. This is necessary for translating between the two during select.select operations to work with our custom objects.
    """

    def __init__(self, config: Config) -> None:
        self.config: Config = config
        super().__init__(self.config)

        # Using Pluggable instead of Peer because server must put itself in these two dictionaries as well. It is not a peer.
        self.socket_to_plug: dict[socket.socket, Pluggable] = {}
        self.plug_to_socket: dict[Pluggable, socket.socket] = {}

        # str is an arbitrary string ID (identifier) for the Pluggable type. A string can be something like a username or the name of a location. As long as the association with it matches the pluggable peer.
        self.peer_to_id: dict[str, Peer] = {}
        self.id_to_peer: dict[Peer, str] = {}

    def remove_connections(self, connection: Peer) -> Peer:
        """
        Removes connections internally, wiping the peer's links between the two internal dictionaries socket_to_pluggable and pluggable_to_socket and also removes them from the active connections.
        """
        peer: Peer = self._purge_id_and_peer(connection)
        result: Peer = self._purge_socket_and_plug(peer)

        return result

    def _purge_socket_and_plug(self, connection: Pluggable) -> Peer:
        """
        Purges internal dictionary links for socket and peer.
        """
        sock = self.plug_to_socket.pop(connection)
        peer = self.socket_to_plug.pop(sock)
        return peer

    def _purge_id_and_peer(self, connection: Peer) -> Peer:
        id: str = self.peer_to_id.pop(connection)
        peer: Peer = self.id_to_peer.pop(id)
        return peer

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
            connections.append(self.socket_to_plug[s])
        return connections

    def all_primitive_sockets(self) -> list[socket.socket]:
        """
        Returns all python socket.sockets in Socket objects for each connection.
        """
        return self.connections_to_sockets(self.socket_to_plug.values())

    def link_socket_and_plug(self, sock: socket.socket, plug: Pluggable) -> None:
        """
        Links a socket and a peer together, both ways.
        """
        self.socket_to_plug[sock] = plug
        self.plug_to_socket[plug] = sock

    def link_id_and_peer(self, id: str, peer: Peer) -> None:
        """
        Links a string ID and a peer together, both ways.
        """
        self.id_to_peer[id] = peer
        self.peer_to_id[peer] = id

    def connected_peers(self) -> list[str]:
        """
        Returns a list of connected peers that are on the server.
        """
        new_list = []
        for id in self.id_to_peer:
            new_list.append(id)
        return new_list

    def peer_from_id(self, id: str) -> Peer:
        """
        Retrieve the associated peer from an ID.
        """
        return self.id_to_peer[id]

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
