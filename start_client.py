from shared.net import *
from client import *
from client.client import Client


def main():
    config = Config(socket_blocking=False)
    client = Client(config, "neo")
    client.run()

    client2 = Client(config, "bento")
    client2.run()

    client3 = Client(config, "kai")
    client3.run()


main()
