"""
Physical application that is the client.
"""

import queue
import select
import sys
from client.database import Database
from shared.crypto import from_base_64
from shared.encryption import AESKey, Locksmith, RSAKey
from shared.protobuf import deserialize
from shared.message import DataMessage, DataMessageChatMessage
from shared.net import *
from shared import *

A_LOGIN = 0
A_LOGOUT = 1
A_CONNECT = 2
A_DISCONNECT = 3
A_SEARCH = 4
A_MESSAGE = 5
A_LIST = 6


COMMAND_BANK: list[str] = ["quit", "chat", "commands", "leave", "who"]


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
    def __init__(
        self,
        config: Config,
        gui_to_client_queue: queue.Queue,
        client_to_gui_queue: queue.Queue,
        username: str = "default_user",
    ) -> None:
        super().__init__(config)

        # checks if we're closing the application
        self.__exit: bool = False

        self.__database: Database = Database()

        # Used for handling message operations from and to a GUI object and vice versa
        self.__gui_to_client_queue: queue.Queue = gui_to_client_queue
        self.__client_to_gui_queue: queue.Queue = client_to_gui_queue

        """
        Chat session variables
        """
        self.__username: str = username
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

    def set_username(self, username: str) -> None:
        self.__username = username

    def _handle_incoming_message(self, message: DataMessage) -> tuple[bool, bytes, str]:
        # server sent messages will always have params coming back AND have response code AND have sender that is "SERVER"

        queue_message: str = None
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

                    queue_message = f"You are now chatting with @{self.__peer}"
                    self.__chat_mode = True
                    # print(self.__database.get_key(self.__peer).serialize())

                # Error occurred
                case 1:
                    queue_message = f"Uh oh! {res_comment}"
                    if res_params == "DISCONNECT":
                        self.__chat_mode = False
                        self.__peer = None

                # Other client disconnected
                case 3:
                    self.__chat_mode = False
                    self.__peer = None
                    queue_message = res_comment

                # server response when requesting a user's public key. This makes the client send their encrypted session key over.
                case 5:
                    self.__database.store_key(message)

                    queue_message = f"Received {self.__peer}'s public key!"

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

                # receives list of mfs back
                case 6:
                    queue_message = f"List of online peers: {res_comment}"

        # In this case, someone is messaging this client, i.e. the sender is not "SERVER". Display messages on the screen.
        else:
            # Any message that isn't blank that comes through is a legit message, else, its a session key.
            if message.sessionkey != "":
                queue_message = f"Received session key!"
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

                queue_message = f"[@{sender}]: {messages}"

        return message_ready, msg, queue_message

    def _parse_command(self, user_input: str) -> tuple[bool, bool, bytes, str]:
        queue_message: str = None
        exited: bool = False
        message_ready: bool = False
        msg: bytes = None

        if len(user_input) == 0:
            return exited, message_ready, msg

        if user_input[0] == "/":
            command, args = sanitize_input(user_input)
            match command:
                case "commands":
                    queue_message = f"Available commands:\n\t{COMMAND_BANK}"
                    message_ready = False

                case "quit":
                    queue_message = "Closing yappin'"
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
                            queue_message = f"you're already chatting with @{args}"
                        else:
                            queue_message = (
                                "disconnect from current chat first by using /leave"
                            )
                        message_ready = False
                    # you cannot chat with yourself
                    elif args == self.__username:
                        queue_message = "you cannot chat with yourself..."
                        message_ready = False
                    elif args != self.__username:
                        queue_message = f"Attempting chat with @{self.__peer}..."

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

                case "leave":
                    queue_message = f"leaving chat with @{self.__peer}"
                    msg = self.make_message(
                        to=None, params=self.__peer, text="", action=A_DISCONNECT
                    )
                    self.__chat_mode = False
                    self.__peer = None
                    message_ready = True

                case "who":
                    msg = self.make_message(to=None, action=A_LIST)
                    message_ready = True
                case _:
                    queue_message = "Invalid command. To see commands, type /commands"

        return exited, message_ready, msg, queue_message

    def set_exit(self, b: bool) -> None:
        self.__exit = b

    def run(self):
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

        x = f"Connected successfully! MOTD: {initial_server_message.response.comment}\n {initial_server_message.params}"

        sys_print(x)

        self.__client_to_gui_queue.put_nowait(x)

        try:
            while not self.__exit:
                queue_message: str = None
                message: bytes = None
                message_ready: bool = False

                read, _write, _error = select.select([self.get_socket()], [], [], 0)

                """
                If the source is from the client network socket, handle it.
                """
                if self.get_socket() in read:
                    data = self.get_data()
                    if data is not None:
                        incoming_message = deserialize(data)

                        # might lead to clashing
                        (
                            message_ready,
                            message,
                            queue_message,
                        ) = self._handle_incoming_message(incoming_message)

                # Check for messages from GUI
                try:
                    user_input = self.__gui_to_client_queue.get_nowait()
                    # Process the message from GUI
                    # ...
                    # check if user input has a command rather than message:
                    if user_input[0] == "/":
                        (
                            self.__exit,
                            message_ready,
                            message,
                            queue_message,
                        ) = self._parse_command(user_input)
                    else:
                        if self.__chat_mode:
                            receiver: str = self.__peer
                            body = self.__session_key.encrypt_and_encode(user_input)

                            message = self.make_message(
                                to=receiver, text=body, action=A_MESSAGE
                            )

                            message_ready = True

                # No messages from GUI
                except queue.Empty:
                    pass

                if queue_message is not None:
                    self.__client_to_gui_queue.put_nowait(queue_message)
                    sys_print(queue_message)

                if message_ready:
                    self.send_data(message)

        except KeyboardInterrupt:
            sys_print("Yappin' closed via KeyboardInterrupt")

            # send quit code to server!
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
