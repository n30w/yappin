from chat import Table
from database import Database
from shared.logger import StdoutLogger
from server.net import *
from shared.net import *
from peer import ChatPeer
from shared.enums import State, Action
from shared.message import DataMessage
from shared.protobuf import ResponseCode, build_message, deserialize, serialize
from shared.chat_types import T, certain_attribute


class ChatServer(Server):
    """Manages clients"""

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.__tables: list[Table] = list()
        self.__online_users: dict[str, ChatPeer] = {}
        self.__database: Database = Database()
        # self.__all_net_sockets: list[Pluggable] = []
        self.__all_net_sockets: dict[str, Pluggable] = {}
        self.__logger: StdoutLogger = StdoutLogger()

    def run(self) -> None:
        self.socket.bind()
        self.socket.listen()

        self.__all_net_sockets["my_addr"] = self

        self.__logger.log(f"Server running @{self.config.BINDING}")

        try:
            while True:
                read_connections = self.read_connections(
                    self.__all_net_sockets.values()
                )

                """
                Check if any users are using their sockets. If they are, handle them accordingly.
                """
                # for user in self.__online_users.values():
                #     if user.get_socket() in read_connections:
                #         data = user.get_data()
                #         message = deserialize(data)
                #         error = self.data_handler(message)

                #         if error is not None:
                #             print(error)
                #             error_message = build_message(ResponseCode.ERROR, new_peer)
                #             runtime_error = user.send_data(error_message)
                #             print(runtime_error)

                """
                A new client wants to connect. Check if their connection is valid. If so, let them in and make a new user. If not, they are not allowed to connect. Delete their socket. Send a transmitted message back. NEW CLIENTS ARE ALWAYS A LOGIN REQUEST!
                """
                if self.get_socket() in read_connections:
                    new_socket, incoming_address = self.accept_connection()

                    self.__logger.log(
                        f"=== INBOUND CONNECTION: @{incoming_address} ==="
                    )

                    # creates a new socket from the incoming connection, with a config
                    config = Config(
                        provided_socket=new_socket,
                        connection_addr=incoming_address,
                        socket_blocking=True,
                    )

                    possible_new_client = Socket(config)

                    # creates a new ChatPeer from the new_client if username is valid
                    new_peer: Exception | ChatPeer = self._attempt_client_login(
                        possible_new_client
                    )

                    # if something fails when validating the connection, make sure to send the client a notification about it. Then delete their socket.
                    if new_peer is Exception:
                        message = build_message(ResponseCode.ERROR, new_peer)
                        possible_new_client.transmit(message)
                        possible_new_client.close()
                        # del new_peer
                    else:
                        # add the new client to the list of online users
                        self.__all_net_sockets[new_peer.username] = new_peer
                        self.__online_users[new_peer.username] = new_peer
                        self.__database.store_config(new_peer)
                        self.__logger.log(f"(LOGIN) @{new_peer.username}")
                        self.__logger.log(
                            f"currently online: {self.__online_users.keys()}"
                        )

        except Exception as e:
            print(f"An error has occurred: {e}")
        finally:
            self.socket.close()

    def _get_table_of(self, username: str) -> tuple[Table, int] | None:
        t: table
        i = 0
        for table in self.__tables:
            if username in table.seats.keys():
                return table, i
            i += 1  # Bad code

        return None

    def _connect_peer_to_peer(self, peer_1: ChatPeer, peer_2: ChatPeer) -> bool:
        """Returns a bool of whether or not creating a table was successful. This is where the key exchange occurs."""
        seated: bool = False

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

        peer_1_key_for_peer_2 = build_message(ResponseCode.SUCCESS, peer_1.key)
        peer_2_key_for_peer_1 = build_message(ResponseCode.SUCCESS, peer_2.key)

        error = peer_1.send_data(peer_2_key_for_peer_1)
        if error is not None:
            print(error)
            return False

        error = peer_2.send_data(peer_1_key_for_peer_2)
        if error is not None:
            print(error)
            return False

        # set the state of the people at the table

        # No idea why i have this. I frogot.
        self.__database.set_user_state(peer_1.username, State.CHATTING)
        self.__database.set_user_state(peer_2.username, State.CHATTING)

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

    def _attempt_client_login(self, new_client: Socket) -> Exception | ChatPeer:
        """
        Based on data retrieved from a new_client socket (an incoming login request), this method either adds a new connection to the list of connections and creates a new ChatPeer OR returns an exception.
        """
        new_peer: ChatPeer

        try:
            raw_data = new_client.receive()
            message = deserialize(raw_data)

            if (
                message.sender in self.__online_users
                or message.sender in self.__database
            ):
                return Exception("username taken")
            else:
                new_peer = ChatPeer(
                    Config(provided_socket=new_client.get(), socket_blocking=False),
                    message.sender,
                    message.pubkey,
                )

                # add username and new ChatPeer to list of online users
                self.__online_users[message.sender] = new_peer

                # update database with user status.
                # new users are added since this is just a dictionary.
                self.__database.set_user_state(message.sender, State.CONNECTED)

                return new_peer

        except Exception as e:
            print(f"Error receiving initial message from new client: {e}")
            return e

    def data_handler(self, message: DataMessage) -> str | None:
        """
        Handles messages to the server. Incoming data bytes SHOULD BE ALREADY deserialized when being consumed by this function.
        """

        # indicates whether an operation succeeded or not
        error: str | None

        # callback function for send
        def by_username(name: str):
            # returns the ChatPeer object of corresponding username
            return self.__online_users[name]

        def _connect() -> str | None:
            peer_1: ChatPeer = self.__online_users[message.sender]
            peer_2: ChatPeer

            # check if the peer even exists in the database first:
            peer_2_exists = message.params in self.__online_users.keys()
            if peer_2_exists:
                peer_2 = self.__online_users[message.params]
            else:
                return "peer not online"

            # check if the peer is chatting with anyone else
            if peer_2.get_state is State.CHATTING:
                return "peer already chatting"

            connected = self._connect_peer_to_peer(peer_1, peer_2)

            if connected:
                return None
            else:
                return "seating issue"

        def _disconnect() -> str | None:
            """
            disconnection from table, they no longer want to chat with each other.
            """

            table: Table
            index: int

            table, index = self._get_table_of(message.sender)

            if table is None:
                return "not seated at a table"

            seated: list[ChatPeer] = table.seats.values()

            # Destroy table
            del self.__tables[index]

            # reset peer states
            # self.__database.set_user_state(seated[0], State.CONNECTED)
            # self.__database.set_user_state(seated[1], State.CONNECTED)

            for peer in seated:
                peer.set_state(State.CONNECTED)

            return None

        def _logout() -> str | None:
            """
            Client full system logout.
            """

            # disconnects the sender from their table first
            if self._is_seated(message.sender):
                error = _disconnect()
            if error is not None:
                return error

            self.__database.set_user_state(message.sender, State.OFFLINE)

            # Delete sender from online users and socket connections

            # THIS HAS TO BE DONE BETTER.
            self.__all_net_sockets[
                self.__database.get_config(message.sender).CONNECTION_ADDR
            ].get_socket().close()

            del self.__online_users[message.sender]

            del self.__all_net_sockets[
                self.__database.get_config(message.sender).CONNECTION_ADDR
            ]

            print(f"@{message.sender} logged out")

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

            send = to(peer_2, by_username)

            # turn the serialized message back into data so that the peer can consume it and transmit the bytes.
            data = serialize(message)

            send(data)

            return None

        # print(f"@{message.sender} requests #{message.action}")

        # read the action
        match message.action:
            case Action.LOGOUT:
                error = _logout()

            case Action.CONNECT:
                error = _connect()

            case Action.DISCONNECT:
                error = _disconnect()

            case Action.MESSAGE:
                error = _message()

            case _:  # How did you even get here dawg
                # send client error response
                error = "no tampering allowed"

        return error

        # send a response code back of SUCCESS
        # if error is not None:
        #     print(message.sender)
        #     peer = self.__online_users[message.sender]
        #     send = to(peer, by_username)
        #     server_message = build_message(ResponseCode.ERROR, error)
        #     data = serialize(server_message)
        #     send(data)


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
def to(dest: any, by: callable):
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
