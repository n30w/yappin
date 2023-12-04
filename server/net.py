import socket, select
from typing import Any, Self
from client.encryption import Key
from shared.enums import State
from shared.types import Address

# Network things

DEFAULT_ADDRESS: Address = ("localhost", 1234)


class Config:
    """
    Config is a parent class that defines configurations for sockets, servers, and anything network related. Also carries socket data.
    """

    def __init__(
        self,
        address_family: socket.AddressFamily = socket.AF_INET,
        socket_kind: socket.SocketKind = socket.SOCK_STREAM,
        binding: Address = "",
        listen_queue: int = 6,
        host_addr: Address = DEFAULT_ADDRESS,
        client_addr: Address = DEFAULT_ADDRESS,
        provided_socket: socket.socket | None = None,
        socket_blocking: bool = True,
    ) -> None:
        # Socket binding address
        self.SOCKET_ADDRESS_FAMILY: socket.AddressFamily = address_family
        self.SOCK_STREAM: socket.SocketKind = socket_kind
        self.BINDING: Address = binding
        self.LISTEN_QUEUE: int = listen_queue
        self.HOST_ADDR: Address = host_addr
        self.CLIENT_ADDR: Address = client_addr
        self.PROVIDED_SOCKET: socket.socket | None = provided_socket
        self.SOCKET_BLOCKING: bool = socket_blocking


class Socket:
    def __init__(self, config: Config) -> Self:
        """
        Initializes and binds a socket to a particular port.
        """

        self.config: Config = config

        if self.config.PROVIDED_SOCKET is not None:
            # load a socket
            self.__python_socket = self.config.PROVIDED_SOCKET
        else:
            self.__python_socket: socket.socket = socket(
                self.config.SOCKET_ADDRESS_FAMILY, self.config.SOCK_STREAM
            )

        if self.config.SOCKET_BLOCKING is True:
            self.__python_socket.setblocking(0)

        return self

    def bind(self) -> None:
        """starts the socket"""
        self.__python_socket.bind(self.config.BINDING)

    def listen(self) -> None:
        """Starts listening and the number of connections to listen to"""
        self.__python_socket.listen(self.config.LISTEN_QUEUE)

    def set_blocking(self) -> None:
        self.__python_socket.setblocking(0)

    def transmit(self, data: bytes) -> RuntimeError | None:
        """
        Transmits data to a peer. Returns none if no error, else, runtime error.
        """

        # Gets the length of the data, then makes a header that is the length of the data. So, int -> bytes conversion.
        data_len = len(data)
        header = data_len.to_bytes(4, byteorder="big")

        # Creates the data to send.
        data_to_send = header + data

        total_sent: int = 0
        while total_sent < len(data_to_send):
            sent = self.__python_socket.send(data_to_send[total_sent:])

            if sent == 0:
                return RuntimeError("Socket connection broken")

            total_sent += sent

        return None

    def _byte_received_data(self, n: int) -> RuntimeError | bytes:
        """
        'byte' here is used as a verb. This method receives socket data from the socket. It is used in receive() to piece together the message. This method also handles partial reads.
        """
        data = bytearray()

        while len(data) < n:
            packet = self.__python_socket.recv(n - len(data))

            if not packet:
                return RuntimeError("Socket connection broken")

            data.extend(packet)

        return bytes(data)

    def receive(self) -> RuntimeError | bytes:
        """
        First reads the header from data received from the socket, then reads the data in given the length of the header.
        """

        # Get header information, reads the first four bytes of the header, since the header length is 4.
        header = self._byte_received_data(4)

        # Now that we have the header, lets turn it into an int, or the data length, that we can use in a method.
        data_length = int.from_bytes(header, byteorder="big")

        # Using the length of the data we have just found, lets read all of the data now.
        data = self._byte_received_data(data_length)
        return data


class Peer:
    def __init__(self, config: Config) -> None:
        self.config: Config = config
        self.__socket: Socket = Socket(self.config)

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
