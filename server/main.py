from server.net import Config
from server.server import ChatServer


def main() -> None:
    config = Config(binding=("localhost", 1234), listen_queue=8, socket_blocking=False)
    server = ChatServer(config)
    server.run()


main()
