# Network things


# Config is a parent class that defines configurations for sockets and servers.
class Config:
    def __init__(self) -> None:
        self.IPV4_ADDR: str = ""
        self.LISTEN_PORT: int = 0


class Socket:
    pass
