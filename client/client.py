"""
Physical application that is the client.
"""

from shared.encryption import Key, Locksmith
from shared.protobuf import Action, serialize
from shared.message import DataMessage
from shared.net import *
from shared import *

A_LOGIN = 0
A_LOGOUT = 1
A_CONNECT = 2
A_DISCONNECT = 3
A_SEARCH = 4
A_MESSAGE = 5


COMMAND_BANK: list[str] = ["quit", "chat", "commands"]


def sanitize_input(input: str) -> tuple[str, str]:
    """
    From user input via command line, sanitizes the input to check for commands.
    """

    # retrieves the first word after the '/' in the input string
    full_line: str = input.split(" ")
    command: str = full_line[0][1:]
    params: str = full_line[1:]

    return command, params


class Client:
    def __init__(self, config: Config, username: str) -> None:
        self.socket = Socket(config)
        self.__config = config
        self.__username = username

    def run(self):
        exited = False

        print(
            f"v(0 o 0)v\n~================~\n  yappin' as @{self.__username}\n~================~"
        )
        make_message = from_sender(self.__username)

        # Initial login handshake
        self.socket.connect()
        msg = make_message("hello", "params", A_MESSAGE)
        self.socket.transmit(msg)

        try:
            while not exited:
                action_queued: bool = False
                command: str
                params: str

                user_input = input("[:>> ")

                if user_input[0] == "/":
                    command, params = sanitize_input(user_input)
                    if command not in COMMAND_BANK:
                        print("invalid command!")
                    else:
                        match command:
                            case "commands":
                                print(f"Available commands:\n\t{COMMAND_BANK}")

                            case "quit":
                                print("[~] Quitting...")
                                action_queued = True
                                exited = True
                                msg = make_message("", "", A_LOGOUT)

                            case "chat":
                                msg = make_message(params, "", A_CONNECT)
                                print(f"[~] Attempting connection with {params}...")
                                action_queued = True

                            case _:
                                print("how'd you even get here what")

                if action_queued:
                    self.socket.transmit(msg)

        except Exception as e:
            print(f"Error: {e}")

        finally:
            self.socket.close()


def from_sender(sender: str):
    dm = DataMessage()
    dm.sender = sender
    public_key: Key
    private_key: Key
    public_key, private_key = Locksmith.generate_keys()
    serialized_pub_key: str = public_key.serialize()

    print(serialized_pub_key)

    def create(params: str, text: str, action: int) -> bytes:
        dm.action = action
        dm.params = params
        dm.messages.append(text.encode())
        dm.pubkey = serialized_pub_key
        return dm.SerializeToString()

    return create
