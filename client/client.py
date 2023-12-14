"""
Physical application that is the client.
"""

import select
import sys
from client.database import Database
from shared.crypto import from_base_64
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

    def _handle_incoming_message(self, message: DataMessage) -> tuple[bool, bytes]:
        # server sent messages will always have params coming back AND have response code AND have sender that is "SERVER"

        message_ready = False
        msg: bytes = None

        sender = message.sender
        res_code = message.response.response
        res_comment = message.response.comment
        res_params = message.params

        if sender == "SERVER":
            # If there is no error, then the server's response is a handshake from another peer.
            match res_code:
                case 0:
                    # check if there exists keys already from the sender. Key is now stored and ready to use.
                    self.__database.store_key(message)
                    self.__peer = res_params

                    # STORE SESSION KEY:

                    sys_print(f"You are now chatting with @{self.__peer}")
                    self.__chat_mode = True
                    # print(self.__database.get_key(self.__peer).serialize())

                # Error occurred
                case 1:
                    sys_print(f"Uh oh! {res_comment}")
                    if res_params == "DISCONNECT":
                        self.__chat_mode = False
                        self.__peer = None

                # Other client disconnected
                case 3:
                    self.__chat_mode = False
                    self.__peer = None
                    sys_print(res_comment)

                # server response when requesting a user's public key. This makes the client send their encrypted session key over.
                case 5:
                    self.__database.store_key(message)

                    sys_print(f"Received {self.__peer}'s public key!")

                    encrypted_session_key = self.__database.get_key(
                        res_params
                    ).encrypt_and_encode(self.__session_key.serialize())

                    # REMEMBER that in this case, res_params or message.params are the chat peer that you are requesting the public keys of.
                    msg = self.make_message(
                        to=self.__peer,
                        text="",
                        action=A_MESSAGE,
                        session_key=encrypted_session_key,
                    )

                    # after getting the server's response, lets send the session key to the other peer back.
                    message_ready = True
                    self.__chat_mode = True

        # In this case, someone is messaging this client, i.e. the sender is not "SERVER". Display messages on the screen.
        else:
            # Any message that isn't blank that comes through is a legit message, else, its a session key.
            if message.sessionkey != "":
                sys_print("Received session key!")
                session_key = self.__private_key.decode_and_decrypt(message.sessionkey)
                session_key = from_base_64(session_key)
                self.__session_key: AESKey = AESKey(session_key)
            else:
                # messages are stored encrypted
                messages: str = ""

                for m in message.messages:
                    # decrypt each message with the sessions' AES key
                    line: str = self.__session_key.decode_and_decrypt(m.body)
                    # messages += m.body
                    messages += line

                print(f"[@{sender}]: {messages}")

        return message_ready, msg

    def _parse_command(self, user_input: str) -> tuple[bool, bool, bytes]:
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
                    message_ready = False

                case "quit":
                    sys_print("Closing yappin'")
                    exited = True
                    msg = self.make_message(
                        to=None,
                        action=A_LOGOUT,
                    )
                    message_ready = True

                case "chat":
                    # disconnect the room before chatting again
                    if self.__chat_mode == True:
                        if self.__peer == args:
                            sys_print(f"you're already chatting with @{args}")
                        else:
                            sys_print(
                                "disconnect from current chat first by using /leave"
                            )
                        message_ready = False
                    # you cannot chat with yourself
                    elif args == self.__username:
                        sys_print("you cannot chat with yourself...")
                        message_ready = False
                    elif args != self.__username:
                        sys_print(f"Attempting connection to @{args}")

                        self.__session_key = Locksmith.generate_session_key()
                        # first check if we already have the peer's public key
                        peer_key = self.__database.get_key(args)

                        if peer_key is not None:
                            # then, encrypt the session key with peer's RSA public key
                            encrypted_session_key: str = peer_key.encrypt_and_encode(
                                self.__session_key.serialize()
                            )

                            msg = self.make_message(
                                params=args,
                                session_key=encrypted_session_key,
                                action=A_CONNECT,
                            )

                        # if we don't have the public key, we're gonna have to request it.
                        else:
                            self.__peer = args
                            msg = self.make_message(params=args, action=A_CONNECT)

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

        # Initial login handshake
        try:
            self.socket.connect()
        except ConnectionRefusedError:
            sys_print("Server offline — try again later")
            return

        msg = self.make_message(to=None, text="", action=A_LOGIN)
        self.send_data(msg)

        data: bytes = self.get_data()
        initial_server_message = deserialize(data)

        print(
            f"\n~================================================~\n v(0 o 0)v yappin' as @{self.__username}\n~================================================~\n"
        )

        sys_print(
            f"Connected successfully! MOTD: {initial_server_message.response.comment}"
        )

        try:
            while not exit:
                message: bytes = None
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

                            # might lead to clashing
                            message_ready, message = self._handle_incoming_message(
                                incoming_message
                            )

                    """
                    Checks for user input. This is on a different socket.
                    """
                    if source is sys.stdin:
                        user_input = input()

                        # check if user input has a command rather than message:
                        if user_input[0] == "/":
                            exit, message_ready, message = self._parse_command(
                                user_input
                            )
                        else:
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
            msg = self.make_message(to=None, action=A_LOGOUT)
            self.send_data(msg)

        except ConnectionResetError:
            sys_print("server died.")

        except ConnectionRefusedError:
            sys_print("server offline.")

        except Exception as e:
            msg = self.make_message(to=None, action=A_LOGOUT)
            self.send_data(msg)

            print(f"Error: {e}")
            traceback.print_exc()

        finally:
            msg = self.make_message(to=None, action=A_LOGOUT)
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
