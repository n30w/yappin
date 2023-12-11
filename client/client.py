"""
Physical application that is the client.
"""

import select
import sys
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
        self.__username = username

        # Encryption
        self.__public_key: Key
        self.__private_key: Key
        self.__public_key, self.__private_key = Locksmith.generate_keys()
        self.__serialized_pub_key: str = self.__public_key.serialize()

    def _handle_incoming_message(self, message: DataMessage) -> None:
        # server sent messages will always have params coming back AND have response code AND have sender that is "SERVER"
        if message.sender == "SERVER":
            # Error has occurred
            if message.response.response == 1:
                print(f"[~] Uh oh! {message.response.comment}")

    def _match_commands(self, user_input: str) -> (bytes, bool):
        exited = False
        msg: bytes = None
        make_message = from_sender(self.__username, self.__serialized_pub_key)

        if user_input[0] == "/":
            command, params = sanitize_input(user_input)
            if command not in COMMAND_BANK:
                print("[~] Invalid command")
            else:
                match command:
                    case "commands":
                        print(f"Available commands:\n\t{COMMAND_BANK}")

                    case "quit":
                        print("[~] Quitting...")
                        exited = True
                        msg = make_message("", "", A_LOGOUT)
                        message_ready = True

                    case "chat":
                        print(f"[~] Attempting connection with {params}...")
                        msg = make_message(params, "", A_CONNECT)

                    case _:
                        print("[~] Invalid command")

        return msg, exited

    def run(self):
        make_message = from_sender(self.__username, self.__serialized_pub_key)

        exit = False

        print("\n~================================================~\n")
        print(f" v(0 o 0)v yappin' as @{self.__username}\n")
        print(f"RSA Public Key: \n{self.__serialized_pub_key}")
        print("~================================================~\n")

        # Initial login handshake
        self.socket.connect()
        # msg = make_message("hello", "params", A_MESSAGE)
        msg = make_message("hello", "params", A_LOGIN)
        self.send_data(msg)
        rec = deserialize(self.get_data())
        sys_print(f"Connected successfully! MOTD: {rec.response.comment}")

        try:
            while not exit:
                message: bytes
                command: str
                params: str
                message_ready: bool = False

                read, _write, _error = select.select(
                    [self.get_socket(), sys.stdin], [], [], 0
                )

                for source in read:
                    """
                    If the source is from the client network socket, handle it.
                    """
                    if source is self.get_socket():
                        data = self.get_data()
                        if data is not None:
                            incoming_message = deserialize(data)
                            self._handle_incoming_message(incoming_message)

                    """
                    Checks for user input. This is on a different socket.
                    """
                    if source is sys.stdin:
                        user_input = input()

                        if user_input[0] == "/":
                            command, params = sanitize_input(user_input)
                            if command not in COMMAND_BANK:
                                sys_print(
                                    "Invalid command. To see commands, type /commands"
                                )
                            else:
                                match command:
                                    case "commands":
                                        sys_print(
                                            f"Available commands:\n\t{COMMAND_BANK}"
                                        )

                                    case "quit":
                                        sys_print("Closing yappin'")
                                        exit = True
                                        msg = make_message("", "", A_LOGOUT)
                                        message_ready = True

                                    case "chat":
                                        sys_print(
                                            f"Attempting connection with {params}"
                                        )
                                        msg = make_message(params, "", A_CONNECT)
                                        message_ready = True

                                    case _:
                                        sys_print("invalid command")

                if message_ready:
                    self.send_data(msg)

        except KeyboardInterrupt:
            sys_print("Yappin' closed via KeyboardInterrupt")

            # send quit code to server!
            msg = make_message("", "", A_LOGOUT)
            self.send_data(msg)

        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()

        finally:
            self.socket.close()


def sys_print(text: str) -> None:
    print(f"[~] {text}")


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
