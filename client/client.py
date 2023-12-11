"""
Physical application that is the client.
"""

import select
from shared.encryption import Key, Locksmith
from shared.protobuf import Action, deserialize, serialize
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


class Client(Pluggable):
    def __init__(self, config: Config, username: str) -> None:
        super().__init__(config)
        self.__config = config
        self.__username = username

        # Encryption
        self.__public_key: Key
        self.__private_key: Key
        self.__public_key, self.__private_key = Locksmith.generate_keys()
        self.__serialized_pub_key: str = self.__public_key.serialize()

    def _handle_incoming_message(self, message: DataMessage) -> None:
        # server sent messages will always have params coming back AND have response code AND have sender that is "SERVER"
        if message.sender == "SERVER":
            print(message.params)

    def run(self):
        make_message = from_sender(self.__username, self.__serialized_pub_key)

        exited = False

        print("\n~================~\n")
        print(f" v(0 o 0)v yappin' as @{self.__username}\n")
        print(f"RSA Public Key: \n{self.__serialized_pub_key}")
        print("~================~\n")

        # Initial login handshake
        self.socket.connect()
        # msg = make_message("hello", "params", A_MESSAGE)
        msg = make_message("hello", "params", A_LOGIN)
        self.socket.transmit(msg)

        try:
            while not exited:
                action_queued: bool = False
                command: str
                params: str

                read, _write, _error = select.select([self.get_socket()], [], [], 0)

                if self.get_socket() in read:
                    data = self.get_data()
                    if data is not None:
                        incoming_message = deserialize(data)
                        print(incoming_message)
                        self._handle_incoming_message(incoming_message)

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
                                print("[~] Invalid command")

                if action_queued:
                    self.send_data(msg)

        except KeyboardInterrupt:
            print("quitting...")

            # send quit code to server!
            msg = make_message("", "", A_LOGOUT)
            self.send_data(msg)

        except Exception as e:
            print(f"Error: {e}")

        finally:
            self.socket.close()


def from_sender(sender: str, pub_key: str):
    dm = DataMessage()
    dm.sender = sender

    def create(params: str, text: str, action: int) -> bytes:
        dm.action = action
        dm.params = params
        dm.messages.append(text.encode())
        dm.pubkey = pub_key
        return dm.SerializeToString()

    return create
