import argparse
import queue
import threading
from client.gui import GUI
from shared.net import *
from client import *
from client.client import Client


def main():
    parser = argparse.ArgumentParser(description="makes a new client")
    parser.add_argument("-n", "--name", type=str, help="username of client")

    args = parser.parse_args()

    gui_to_client_queue = queue.Queue()
    client_to_gui_queue = queue.Queue()

    config = Config(socket_blocking=False)

    def new_client(username) -> Client:
        return Client(config, gui_to_client_queue, client_to_gui_queue, username)

    gui = GUI(gui_to_client_queue, client_to_gui_queue, new_client)
    gui.run()


if __name__ == "__main__":
    main()
