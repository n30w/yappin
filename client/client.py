"""
Physical application that is the client.
"""

import select
import sys
from client.database import Database
from shared.encryption import AESKey, Locksmith, RSAKey
from shared.protobuf import Action, deserialize, serialize
from shared.message import DataMessage, DataMessageChatMessage
from shared.net import *
from shared import *

A_LOGIN = 0
A_LOGOUT = 1
A_CONNECT = 2
A_DISCONNECT = 3
A_SEARCH = 4
A_MESSAGE = 5


COMMAND_BANK: list[str] = ["quit", "chat", "commands", "switch", "leave", "who"]


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
        self.__database: Database = Database()

        """
        Chat session variables
        """
        self.__username = username
        self.__peer: str = ""
        self.__chat_mode: bool = False

        """
        Encryption
        """
        self.__public_key: RSAKey
        self.__private_key: RSAKey

        # When chatting, this is the AES session key used for decrypting messages.
        self.__session_key: AESKey

        (
            self.__public_key,
            self.__private_key,
        ) = Locksmith.generate_rsa_keys()

        self.__serialized_pub_key: str = self.__public_key.serialize()

        """
        Message creation callback
        """
        self.make_message = from_sender(self.__username, self.__serialized_pub_key)

    def _handle_incoming_message(self, message: DataMessage) -> None:
        # server sent messages will always have params coming back AND have response code AND have sender that is "SERVER"

        sender = message.sender
        res_code = message.response.response
        res_comment = message.response.comment

        if sender == "SERVER":
            # If there is no error, then the server's response is a handshake from another peer.
            if res_code == 0:
                # check if their exists keys already from the sender. Key is now stored and ready to use.
                self.__database.store_key(message)
                self.__peer = message.params

                # STORE SESSION KEY:

                # GET MESSAGE TEXT — in this case, it is the AES encryption key

                sys_print(f"You are now chatting with @{self.__peer}")
                self.__chat_mode = True
                # print(self.__database.get_key(self.__peer).serialize())

            # Error has occurred
            elif res_code == 1:
                sys_print(f"Uh oh! {res_comment}")
                if message.params == "DISCONNECT":
                    self.__chat_mode = False
                    self.__peer = None

        # In this case, someone is messaging this client, i.e. the sender is not "SERVER". Display messages on the screen.
        else:
            # messages are stored encrypted
            self.__database.store_message(message)

            messages: str = ""

            for m in message.messages:
                # decrypt each message with the sessions' AES key
                line: str = self.__session_key.decode_and_decrypt(m)
                # messages += m.body
                message += line

            print(f"[@{sender}]: {messages}")

    def _parse_command(self, user_input: str) -> (bool, bool, bytes):
        exited: bool = False
        message_ready: bool = False
        msg: bytes = None

        if len(user_input) == 0:
            return exited, message_ready, msg

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
                        self.__session_key = Locksmith.generate_session_key()

                        # Encrypt the session key with peer's

                        msg = self.make_message(
                            params=args,
                            text=self.__session_key.serialize(),
                            action=A_CONNECT,
                        )

                        message_ready = True

                case "switch":
                    pass

                case "leave":
                    sys_print(f"leaving chat with @{self.__peer}")
                    msg = self.make_message(
                        to=None, params=self.__peer, text="", action=A_DISCONNECT
                    )
                    self.__chat_mode = False
                    self.__peer = None
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

        initial_server_message = deserialize(self.get_data())

        sys_print(
            f"Connected successfully! MOTD: {initial_server_message.response.comment}"
        )

        try:
            while not exit:
                message: bytes
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

                        if self.__chat_mode:
                            receiver: str = self.__peer
                            body = self.__session_key.encrypt_and_encode(user_input)

                            msg = self.make_message(
                                to=receiver, text=body, action=A_MESSAGE
                            )

                            # message_ready = True
                            self.send_data(msg)

                if message_ready:
                    self.send_data(message)

        except KeyboardInterrupt:
            sys_print("Yappin' closed via KeyboardInterrupt")

            # send quit code to server!
            # msg = make_message("", "", A_LOGOUT)
            msg = self.make_message(to=None, params="", text="bye", action=A_LOGOUT)
            self.send_data(msg)

        except ConnectionResetError:
            sys_print("server died.")

        except ConnectionRefusedError:
            sys_print("server offline.")

        except Exception as e:
            msg = self.make_message(to=None, params="", text="bye", action=A_LOGOUT)
            self.send_data(msg)

            print(f"Error: {e}")
            traceback.print_exc()

        finally:
            msg = self.make_message(to=None, params="", text="bye", action=A_LOGOUT)
            self.send_data(msg)

            self.socket.close()


def sys_print(text: str) -> None:
    print(f"[~] {text}")


# functional builder pattern to send a message
def from_sender(sender: str, pub_key: str):
    def create(
        to: str = None,
        params: str = "",
        text: str = None,
        action: int = 9,
        session_key: str = "",
    ) -> bytes:
        dm = DataMessage(
            sender=sender,
            action=action,
            params=params,
            pubkey=pub_key,
            sessionkey=session_key,
            messages=DataMessageChatMessage(
                sender=sender, receiver=to, body=text, date=""
            ),
        )

        return dm.SerializeToString()

    return create
