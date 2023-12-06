import socket
from typing import Self, Sequence
from server.chat import Table
from server.database import Database
from server.net import Config, Server
from server.peer import ChatPeer, Peer
from shared.enums import State, Action
from shared.protobuf import deserialize, serialize
from shared.types import T, certain_attribute


class ChatServer(Server):
    """Manages clients"""

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.__tables: list[Table] = list()
        self.__online_users: dict[str, ChatPeer] = {}
        self.__database: Database = Database()

    def _get_table_of(self, username: str) -> (Table, int) | None:
        t: table
        i = 0
        for table in self.__tables:
            if username in table.seats.keys():
                return table, i
            i += 1  # Bad code

        return None

    def run(self) -> None:
        """
        TODO: Add socket logic and select statements.
        Note that select.select reads the sockets and returns them, in a list. That list has all of the sockets that the server can then operate on. For each item in the list, the server decides what to do with it given certain conditions.
        """
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

    def _is_seated(self, username: str) -> bool:
        """Checks if a bozo is sitting at any table"""
        for table in self.__tables:
            if username in table.get_seated_info():
                return True

        return False

    def data_handler(self, data: bytes, accepted_connection: socket.socket) -> None:
        """
        Handles messages to the server. Incoming data bytes SHOULD BE ALREADY deserialized when being consumed by this function.
        """
        # deserialize incoming protobuf to check what the header is.
        # Please move this to somewhere better.
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

        def _connect() -> str | None:
            peer_1 = self.__online_users[message.sender]
            peer_2 = self.__online_users[message.params]

            connected = self.connect_peer_to_peer(peer_1, peer_2)

            if connected:
                return None
            else:
                return "peer offline or already chatting"

        def _disconnect() -> str | None:
            [table, index]: [Table, int] = self._get_table_of(message.sender)

            if table is None:
                return "not seated at a table"

            seated = table.seats.keys()

            # Destroy table
            del self.__tables[index]

            # reset peer states
            self.__database.set_user_state(seated[0], State.CONNECTED)
            self.__database.set_user_state(seated[1], State.CONNECTED)

            return None

        def _logout() -> str | None:
            # disconnects the sender from their table first
            if self._is_seated(message.sender):
                error = _disconnect()
            if error is not None:
                return error

            self.__database.set_user_state(message.sender, State.OFFLINE)
            del self.__online_users[message.sender]

            return None

        def _message() -> str | None:
            peer_1 = self.__online_users[message.sender]

            t: table
            # check if bozo is seated
            seated: bool = False

            for table in self.__tables:
                if peer_1.username in table.get_seated_info():
                    seated = True
                    t = table
                    break

            # if not seated, return error
            if not seated:
                return "not seated"

            # if seated, forward the message to the recipient
            peer_2 = t.get_peer(peer_1.username)

            def by_username(name: str):
                # returns the ChatPeer object of corresponding username
                return self.__online_users[name]

            send = to(peer_2, by_username)
            send(data)

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

        # send a response code back of SUCCESS
        if error is not None:
            # Access server socket
            pass
        else:  # send response code of ERROR with reason
            pass


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


# Dispatches a message to send off
def to(dest: any, by: function):
    """
    Functional approach to routing messages between peers and server internals.

    Args:
        dest -- destination to send the object to
        by -- function to retrieve the object that will consume
    """
    receiver = by(dest)

    def route(what: any):
        receiver.consume(what)

    return route
