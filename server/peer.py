from server.net import Config

# Defines peers in the server, aka the clients that connect to the server.


# Key represents the Public Key that each peer posses.
class Key:
    def __init__(self) -> None:
        pass


class Peer:
    def __init__(self, config: Config, key: Key) -> None:
        self.config: Config = config
        self.key: Key = key
