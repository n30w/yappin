"""
Physical application that is the client.
"""

import select
import sys
from client.database import Database
from shared.encryption import Key, Locksmith, deserialize_key
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


COMMAND_BANK: list[str] = ["quit", "chat", "commands", "switch", "leave"]


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
        self.__chat_mode: bool = (
            False  # checks whether or not this client is connected and chatting
        )

        # person you're talking to
        self.__peer: str = ""

        self.__database: Database = Database()

        # Encryption
        self.__public_key: Key
        self.__private_key: Key
        self.__public_key, self.__private_key = Locksmith.generate_keys()
        self.__serialized_pub_key: str = self.__public_key.serialize()

        # message creation callback
        self.make_message = from_sender(self.__username, self.__serialized_pub_key)

    def _handle_incoming_message(self, message: DataMessage) -> None:
        # server sent messages will always have params coming back AND have response code AND have sender that is "SERVER"

        sender = message.sender
        res_code = message.response.response
        res_comment = message.response.comment

        if sender == "SERVER":
            # If there is no error, then the server's response is a handshake from another peer.
            if res_code == 0:
                # check if there exists keys already from the sender. Key is now stored and ready to use.
                self.__database.store_key(message)
                self.__peer = message.params
                sys_print(f"You are now chatting with @{self.__peer}")
                self.__chat_mode = True
                # print(self.__database.get_key(self.__peer).serialize())

            # Error has occurred
            elif res_code == 1:
                sys_print(f"Uh oh! {res_comment}")
                if message.params == "DISCONNECT":
                    self.__chat_mode = False

        # In this case, someone is messaging this client. Display messages on the screen.
        else:
            # messages are stored encrypted
            self.__database.store(message)
            # decrypt message
            messages: str = f"{sender}: "

            for m in message.messages:
                decrypted = Locksmith.decrypt(self.__private_key, m.body)
                messages += decrypted + "\n"

            print(messages)

    def _parse_command(self, user_input: str) -> (bool, bool, bytes):
        exited: bool = False
        message_ready: bool = False
        msg: bytes = None

        if user_input[0] == "/":
            command, args = sanitize_input(user_input)
            if command not in COMMAND_BANK:
                sys_print("Invalid command. To see commands, type /commands")
                return exited, message_ready, msg

            match command:
                case "commands":
                    sys_print(f"Available commands:\n\t{COMMAND_BANK}")

                case "quit":
                    sys_print("Closing yappin'")
                    exited = True
                    msg = self.make_message(
                        to=None,
                        params="",
                        text="bye",
                        action=A_LOGOUT,
                    )
                    message_ready = True

                case "chat":
                    # you cannot chat with yourself
                    if args == self.__username:
                        sys_print("you cannot chat with yourself...")
                        message_ready = False
                    elif args != self.__username:
                        sys_print(f"Attempting connection to @{args}")
                        msg = self.make_message(params=args, text="", action=A_CONNECT)
                        message_ready = True

                case "switch":
                    pass

                case "leave":
                    sys_print(f"leaving chat with @{self.__peer}")
                    msg = self.make_message(
                        to=None, params=self.__peer, text="", action=A_DISCONNECT
                    )
                    self.__chat_mode = False
                    message_ready = True

                case _:
                    sys_print("invalid command")

        return exited, message_ready, msg

    def run(self):
        exit = False

        print("\n~================================================~\n")
        print(f" v(0 o 0)v yappin' as @{self.__username}\n")
        print(f"RSA Public Key: \n{self.__serialized_pub_key}")
        print("~================================================~\n")

        # Initial login handshake
        self.socket.connect()
        msg = self.make_message(to=None, text="", action=A_LOGIN)
        self.send_data(msg)

        # HANDLE THIS: In the event that the username is invalid, make sure to exit gracefully
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
                        exit, message_ready, message = self._parse_command(user_input)
                        # if self.__chat_mode:
                        #     # package the message
                        #     # transmit it to server

                        #     receiver: str = self.__peer

                        #     sender_pub_key: Key = self.__database.get_key(receiver)

                        #     message_body = Locksmith.encrypt(sender_pub_key, user_input)

                        #     msg = self.make_message(
                        #         to=receiver, text=message_body, action=A_MESSAGE
                        #     )

                        #     message_ready = True

                if message_ready:
                    self.send_data(message)

        except KeyboardInterrupt:
            sys_print("Yappin' closed via KeyboardInterrupt")

            # send quit code to server!
            # msg = make_message("", "", A_LOGOUT)
            msg = self.make_message(to=None, params="", text="bye", action=A_LOGOUT)
            self.send_data(msg)

        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()

        finally:
            msg = self.make_message(to=None, params="", text="bye", action=A_LOGOUT)
            self.send_data(msg)

            self.socket.close()


def sys_print(text: str) -> None:
    print(f"[~] {text}")


def from_sender(sender: str, pub_key: str):
    dm = DataMessage()
    dm.sender = sender

    def create(
        to: str = None, params: str = "", text: str = None, action: int = 9
    ) -> bytes:
        dm.action = action
        dm.params = params
        dm.pubkey = pub_key

        if to is not None:
            dm.messages[0].body = text
            dm.messages[0].sender = sender
            dm.messages[0].receiver = to
            dm.messages[0].date = ""
        else:
            dm.messages.append(text.encode())

        return dm.SerializeToString()

    return create
