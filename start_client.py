import argparse
from shared.net import *
from client import *
from client.client import Client


def main():
    parser = argparse.ArgumentParser(description="makes a new client")
    parser.add_argument("-n", "--name", type=str, help="username of client")

    args = parser.parse_args()

    config = Config(socket_blocking=False)
    client = Client(config, args.name)
    client.run()


if __name__ == "__main__":
    main()
