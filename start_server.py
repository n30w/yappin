import sys
import os

# Add the library folder to the system path
sys.path.append(os.path.abspath("./server"))


from chatserver import ChatServer
from net import Config


def main() -> None:
    config = Config(binding=("localhost", 1234), listen_queue=8, socket_blocking=False)
    server = ChatServer(config)
    server.run()


main()
