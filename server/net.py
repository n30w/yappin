from shared.types import Address

# Network things


class Config:
    """
    Config is a parent class that defines configurations for sockets, servers, and anything network related.
    """

    def __init__(self) -> None:
        self.HOST_ADDR: Address
        self.CLIENT_ADDR: Address


class Socket:
    pass
