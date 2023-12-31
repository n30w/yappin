import socket
import time
import traceback
from typing import Optional
from shared.chat_types import Address


DEFAULT_ADDRESS: Address = ("127.0.0.1", 1234)

"""
Socket transmission and receiving functions. Handles partial reads.
"""


def transmit(sock: socket.socket, data: bytes) -> None:
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
        sent = sock.send(data_to_send[total_sent:])

        if sent == 0:
            raise RuntimeError("Socket connection broken")

        total_sent += sent

    return None


def receive(sock: socket.socket) -> bytes | None:
    """
    First reads the header from data received from the socket, then reads the data in given the length of the header.
    """

    def byte_received_data(sock: socket.socket, n: int) -> Optional[bytes]:
        data = bytearray()
        retries = 0
        max_retries = 5
        retry_delay = 0.2

        while len(data) < n:
            try:
                packet = sock.recv(n - len(data))
                if not packet:  # Connection has been closed
                    return None
                data.extend(packet)
            except BlockingIOError:
                if retries >= max_retries:
                    return None  # Max retries reached, return None
                time.sleep(retry_delay)  # Wait before retrying
                retries += 1
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None

        return bytes(data)

    # Get header information, reads the first four bytes of the header, since the header length is 4.
    header = byte_received_data(sock, 4)

    if header is None:
        # raise RuntimeError("Failed to receive data: connection error - no header")
        # Bozo disconnected
        return

    # Now that we have the header, lets turn it into an int, or the data length, that we can use in a method.
    data_length = int.from_bytes(header, byteorder="big")

    # Using the length of the data we have just found, lets read all of the data now.
    data = byte_received_data(sock, data_length)

    if data is None:
        return
        # raise RuntimeError("Failed to receive data: connection error - no data")

    return data


class Config:
    """
    Config is a parent class that defines configurations for sockets, servers, and anything network related. Also carries socket data.
    """

    def __init__(
        self,
        address_family: socket.AddressFamily = socket.AF_INET,
        socket_kind: socket.SocketKind = socket.SOCK_STREAM,
        binding: Address = ("", 0),
        listen_queue: int = 6,
        host_addr: Address = DEFAULT_ADDRESS,
        client_addr: Address = DEFAULT_ADDRESS,
        provided_socket: socket.socket | None = None,
        socket_blocking: bool = False,
        connection_addr: str = "",
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
        self.CONNECTION_ADDR: str = connection_addr


class Socket:
    """
    Socket wraps functionality for Python sockets.
    """

    def __init__(self, config: Config) -> None:
        """
        Initializes and binds a socket to a particular port.
        """

        self.config: Config = config

        if self.config.PROVIDED_SOCKET is not None:
            # load a socket
            self.python_socket = self.config.PROVIDED_SOCKET
        else:
            self.python_socket: socket.socket = socket.socket(
                self.config.SOCKET_ADDRESS_FAMILY, self.config.SOCK_STREAM
            )

        if self.config.SOCKET_BLOCKING is True:
            self.python_socket.setblocking(0)

    def get(self) -> socket.socket:
        """
        Returns the internal python socket for config purposes.
        """
        return self.python_socket

    def bind(self) -> None:
        """starts the socket"""
        if self.config.BINDING == ("", 0):
            raise ValueError("invalid binding address")
        self.python_socket.bind(self.config.BINDING)

    def listen(self) -> None:
        """Starts listening and the number of connections to listen to"""
        if self.config.LISTEN_QUEUE < 2:
            raise ValueError("listen_queue must be greater than 1")
        self.python_socket.listen(self.config.LISTEN_QUEUE)

    def accept(self) -> tuple[socket.socket, Address]:
        """
        Accepts a socket from self.__python_socket and returns a new accepted socket from that socket.
        """
        new_socket: socket.socket
        address: Address
        new_socket, address = self.python_socket.accept()
        return (new_socket, address)

    def close(self) -> None:
        self.python_socket.close()

    def set_blocking(self) -> None:
        self.python_socket.setblocking(0)

    def connect(self) -> None:
        self.python_socket.connect(self.config.HOST_ADDR)

    def transmit(self, data: bytes) -> RuntimeError | None:
        transmit(self.python_socket, data)

    def receive(self) -> bytes | None:
        return receive(self.python_socket)


class Pluggable:
    """
    Defines anything that has a 'socket', something that is pluggable.
    """

    def __init__(self, config: Config) -> None:
        self.socket = Socket(config)

    def get_socket(self) -> socket.socket:
        return self.socket.python_socket

    def get_data(self) -> Optional[bytes]:
        """
        Pluggable class method that retrieves data from the socket.
        """
        return self.socket.receive()

    def send_data(self, data: bytes) -> RuntimeError | None:
        """
        Pluggable class method that sends data to transmit it to a socket
        """
        error = self.socket.transmit(data)
        return error

    def accept_connection(self) -> tuple[socket.socket, str]:
        new_socket: socket.socket
        ip: Address

        new_socket, ip = self.socket.accept()
        return (new_socket, ip[0])
