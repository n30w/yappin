import socket
from shared.types import Address

# Network things


class Config:
    """
    Config is a parent class that defines configurations for sockets, servers, and anything network related.
    """

    def __init__(self) -> None:
        # Socket binding address
        self.BINDING: Address
        self.LISTEN_QUEUE: int = 5
        self.HOST_ADDR: Address
        self.CLIENT_ADDR: Address


class Socket:
    def __init__(self, config: Config) -> None:
        """
        Initializes and binds a socket to a particular port.
        """
        self.config: Config = config

        self.python_socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.python_socket.bind(self.config.BINDING)
