import socket, select
from typing import Any, Self
from client.encryption import Key
from shared.enums import State
from shared.types import Address

# Network things


class Config:
    """
    Config is a parent class that defines configurations for sockets, servers, and anything network related.
    """

    def __init__(
        self,
        address_family: socket.AddressFamily = socket.AF_INET,
        socket_kind: socket.SocketKind = socket.SOCK_STREAM,
    ) -> None:
        # Socket binding address
        self.SOCKET_ADDRESS_FAMILY: socket.AddressFamily = address_family
        self.SOCK_STREAM: socket.SocketKind = socket_kind
        self.BINDING: Address
        self.LISTEN_QUEUE: int = 6
        self.HOST_ADDR: Address
        self.CLIENT_ADDR: Address


class Socket:
    def __init__(self, config: Config) -> Self:
        """
        Initializes and binds a socket to a particular port.
        """

        self.config: Config = config
        self.__python_socket: socket = socket(
            self.config.SOCKET_ADDRESS_FAMILY, self.config.SOCK_STREAM
        )

        return self

    def bind(self) -> None:
        """starts the socket"""
        self.__python_socket.bind(self.config.BINDING)

    def listen(self) -> None:
        """Starts listening and the number of connections to listen to"""
        self.__python_socket.listen(self.config.LISTEN_QUEUE)

    def set_blocking(self) -> None:
        self.__python_socket.setblocking(0)

    def transmit(self) -> None:
        """Transmits data"""


class Peer:
    def __init__(self, config: Config, key: Key) -> None:
        self.config: Config = config
        self.__socket: Socket = Socket(self.config).bind()

        # a peer is only initialized when it is connected
        self.__state: State = State.CONNECTED

    def consume(self, obj) -> None:
        """
        Consumes either a Message or an Action and does something with it.
        """
        pass

    def get_state(self) -> State:
        """Gets the state"""
        return self.__state

    def set_state(self, state: State) -> State:
        """Sets and returns the state it was set to"""
        self.__state = state
        return self.__state


class Server:
    """Class that defines the 'network' component of what a server is. The thing that calls the shots."""

    def __init__(self, config: Config) -> None:
        self.config: Config = config
        self.server_socket: Socket = Socket(config)
        self.connections: list[Peer] = list()

    def __read_connections(self, connections: list) -> list[Any]:
        """Reads connections using select.select, returns the list of read connections."""
        read, _write, _error = select.select(connections, [], [])
        return read

    def listen_and_serve(self) -> None:
        self.server_socket.bind()
        self.server_socket.listen()

        socket_connections: list[Socket] = [self.server_socket]

        while True:
            read_connections: list[Any] = self.__read_connections(socket_connections)

            for peer in read_connections:
                if peer is self.server_socket:
                    print("")
