from typing import Self, Sequence
from server.chat import Table
from server.database import Database
from server.net import Config, Server
from server.peer import ChatPeer, Peer
from shared.enums import State, Action
from shared.protobuf import deserialize, serialize
from shared.types import T, certain_attribute


class ChatServer(Server):
    """Manages the state of clients."""

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.__router: Router = Router()
        self.__tables: list[Table] = list()
        self.__online_users: dict[str, ChatPeer] = {}
        self.__database: Database = Database()
        # Database?

    def run(self) -> None:
        """
        TODO: Add socket logic and select statements.
        Note that select.select reads the sockets and returns them, in a list. That list has all of the sockets that the server can then operate on. For each item in the list, the server decides what to do with it given certain conditions.
        """
        pass

    def list_connections() -> list:
        pass

    def connect_peer_to_peer(self, peer_1: ChatPeer, peer_2: ChatPeer) -> bool:
        """Returns a bool of whether or not creating a table was successful"""
        seated: bool = False

        # chatting OR table they are sitting at is already the one with the other peer.
        if peer_2.get_state() == State.CHATTING or peer_2.get_state() == State.OFFLINE:
            return False  # Cannot connect to someone who is already chatting
        else:
            table: Table = Table()

            # seat our guests at a table
            seated = table.seat(peer_1)
            if not seated:
                return False
            seated = table.seat(peer_2)
            if not seated:
                return False

            # facilitate key handshake
            table.key_ring.append(peer_1.key, peer_2.key)

            self.__router.select(table.key_ring[0]).route_to(peer_2)
            self.__router.select(table.key_ring[1]).route_to(peer_1)

            # Everyone is now chatting-able
            peer_1.set_state(State.CHATTING)
            peer_2.set_state(State.CHATTING)

            # add the created table to a list of tables
            self.__tables.append(table)

            return True

    def data_handler(self, data: bytes) -> None:
        """Handles messages to the server."""

        # Forward, Do, Respond – three functions that determine what the server does with a message. All result in a bool, success or failure.

        # deserialize incoming protobuf
        message = deserialize(data)

        # indicates whether an operation succeeded or not
        error: str | None = False

        def _login() -> str | None:
            """
            Route to login a user. Since logging in is the first thing that is sent during a client handshake, this function must check if the username is taken or not. This can deny connections.

            returns None or str. If not None, string describes the error.
            """
            if (
                message.sender in self.__online_users
                or message.sender in self.__database
            ):
                return "username taken"
            else:
                # add username and new ChatPeer to list of online users
                self.__online_users[message.sender] = ChatPeer(
                    Config(provided_socket=accepted_connection, socket_blocking=False),
                    message.sender,
                    message.pubkey,
                )

                # update database with user status.
                # new users are added since this is just a dictionary.
                self.__database.set_user_state(message.sender, State.CONNECTED)

            return None

        def _logout() -> str | None:
            pass

        def _connect() -> str | None:
            peer_1 = self.__online_users[message.sender]
            peer_2 = self.__online_users[message.params]

            connected = self.connect_peer_to_peer(peer_1, peer_2)

            if connected:
                return None
            else:
                return "peer offline or already chatting"

        def _disconnect() -> str | None:
            pass

        def _search() -> str | None:
            """Look through chat history and send it off"""
            found: bool
            if found:
                return None
            else:
                return "keyword or phrase not found"

        def _message() -> str | None:
            peer_1 = self.__online_users[message.sender]

            # check if peer_1 is seated

            # if not seated, return error

            # if seated, forward the message to the recipient

            return None

        # read the action
        match message.action:
            case Action.LOGIN:
                error = _login()

            case Action.LOGOUT:
                error = _logout()

            case Action.CONNECT:
                error = _connect()

            case Action.DISCONNECT:
                error = _disconnect()

            case Action.SEARCH:
                error = _search()

            case Action.MESSAGE:
                error = _message()

            case _:  # How did you even get here dawg
                # send client error response
                error = "no tampering allowed"

        # serialize data again to send it off somewhere
        forwarded_message = serialize(data)

        # send a response code back of SUCCESS
        if error is not None:
            # Access server socket
            pass
        else:  # send response code of ERROR with reason
            pass


class Router:
    """
    Routes data between internal server components. Does NOT transmit anything via network connections, that is what net module is for. This is an internal server class.

    Rather than taking a functional approach, this is more-so OOP because the object, in this case Router, is the doer of the action rather than a group of imperative functions.
    """

    def __init__(self) -> None:
        self.__selection: T = None

    def select(self, target: T) -> Self:
        """
        Selects a target, i.e. the thing or the "what" that will be routed.
        """

        self.__selection = target
        return self

    def route_to(self, dest: T) -> Self:
        """
        Routes an object to an internal destination. Returns a bool of whether the routing was possible or not. Wipes internal buffer after destination consumes the object.
        """

        dest.consume(self.__selection)
        self.__selection = None
        return self


def tabulate_guests(tables: list[Table]) -> list[ChatPeer]:
    """
    Returns the list of all peers that are logged into the server.
    """

    peers: list[ChatPeer] = []

    for table in tables:
        peers.extend(table.seats)

    return peers


def create_list(of: list[T], by: certain_attribute) -> list[T]:
    """
    ### Args
        of: T -- target type/object to tabulate. Usually a container.
        by: function -- function operation to retrieve something from the "what". Like an object attribute.
    """

    want: list[T] = []

    for obj in of:
        want.append(by(obj))

    return want
