import traceback
from chat import Table
from database import Database
from shared.logger import StdoutLogger
from server.net import *
from shared.net import *
from peer import ChatPeer
from shared.enums import Action, State, ACTIONS
from shared.message import DataMessage
from shared.protobuf import ResponseCode, build_server_response, deserialize, serialize
from shared.chat_types import T, certain_attribute


class ChatServer(Server):
    """Manages clients"""

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.__tables: list[Table] = list()
        self.__online_users: dict[str, ChatPeer] = {}
        self.__database: Database = Database()

    def run(self) -> None:
        self.socket.bind()
        self.socket.listen()

        """ IMPORTANT! Link own socket to socket and plug """
        self.active_connections["my_addr"] = self
        self.link_socket_and_plug(self.get_socket(), self)

        StdoutLogger.log(f"Server running @{self.config.BINDING}")

        try:
            while True:
                sockets: list[socket.socket] = self.connections_to_sockets(
                    self.active_connections.values()
                )

                read, _write, _error = select.select(sockets, [], [])

                for sock in read:
                    if sock is self.get_socket():
                        """
                        In this case, a new client wants to connect. Check if their connection is valid. If so, let them in and make a new user. If not, they are not allowed to connect. Delete their socket. Send a transmitted message back. NEW CLIENTS ARE ALWAYS A LOGIN REQUEST!
                        """

                        self._handle_incoming_connection(sock)

                    else:
                        """
                        Handle activity from other sockets that have activity.
                        """

                        self._handle_client_message(sock)

        except KeyboardInterrupt:
            # Close all sockets
            pass
        except Exception as e:
            print(f"An error has occurred: {e}")
            traceback.print_exc()
        finally:
            self.socket.close()

    def _handle_incoming_connection(self, sock: socket.socket) -> None:
        # new_socket, incoming_address = self.accept_connection()
        new_socket, incoming_address = sock.accept()
        new_socket.setblocking(False)

        StdoutLogger.log(f"=== INBOUND CONNECTION: @{incoming_address} ===")

        # creates a new socket from the incoming connection, with a config
        config = Config(
            provided_socket=new_socket,
            connection_addr=incoming_address[0],
            socket_blocking=False,
        )

        new_client = Socket(config)
        new_client.config.SOCKET_BLOCKING = False

        raw_data = receive(new_socket)
        message = deserialize(raw_data)

        new_peer = ChatPeer(
            Config(provided_socket=new_client.get(), socket_blocking=False),
            username=message.sender,
            key=message.pubkey,
        )

        # creates a new ChatPeer from the new_client if username is valid
        # new_peer: ChatPeer = self._attempt_client_login(possible_new_client)
        self.link_socket_and_plug(new_peer.get_socket(), new_peer)
        self.active_connections[new_peer.username] = new_peer
        self.__online_users[new_peer.username] = new_peer
        self.__database.store_config(new_peer)
        StdoutLogger.user_action(new_peer.username, ACTIONS[message.action])
        StdoutLogger.log(f"currently online: {self.__online_users.keys()}")

        # validate the connection and make sure there is no duplicate username

        # if something fails when validating the connection, make sure to send the client a notification about it. Then delete their socket.
        # if new_peer is Exception:
        #     # message = build_message(ResponseCode.ERROR, new_peer)
        #     # possible_new_client.transmit(message)
        #     possible_new_client.close()
        #     # del new_peer
        # else:
        # add the new client to the list of online users

    def _handle_client_message(self, sock: socket.socket) -> None:
        # read the data out of the connection (the socket)
        connection: Pluggable = self.socket_to_pluggable[sock]
        data = connection.get_data()

        if data is not None:
            message = deserialize(data)
            return_message = self.data_handler(message, connection)

        # An error occurred, so send data back to client.
        if return_message is not None:
            response = build_server_response(1, return_message)
            connection.send_data(response)

        return None

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

    def _attempt_client_login(self, new_client: Socket) -> ChatPeer:
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
            traceback.print_exc()

    def data_handler(self, message: DataMessage, connection: Pluggable) -> str | None:
        """
        Handles messages to the server. Incoming data bytes SHOULD BE ALREADY deserialized when being consumed by this function.
        """

        # indicates whether an operation succeeded or not

        # callback function for send
        def by_username(name: str):
            # returns the ChatPeer object of corresponding username
            return self.__online_users[name]

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

        StdoutLogger.user_action(message.sender, ACTIONS[message.action])

        # read the action
        match message.action:
            case 1:  # I don't know why I can't use Action
                """
                Client full system logout.
                """

                # internal database cleanup
                self.__database.set_user_state(message.sender, State.OFFLINE)

                # Delete sender from online users and socket connections
                self.__online_users.pop(message.sender)
                self.active_connections.pop(message.sender)

                final = self.purge_links(connection)
                final.socket.close()

                return None

            case 2:
                """
                Connect one peer to another
                """

                peer_1: ChatPeer = self.__online_users.get(message.sender)
                peer_2: ChatPeer

                # check if other user is even online
                if message.params not in self.__online_users.keys():
                    StdoutLogger.log(
                        f"@{message.sender} attempted connection to non-existent user @{message.params}"
                    )
                    return f"@{message.params} is not online or does not exist"
                else:
                    peer_2 = self.__online_users.get(message.params)

                # get state of other user
                if peer_2.get_state() is State.CHATTING:
                    StdoutLogger.log(
                        f"@{message.sender} attempted connection to CHATTING user @{message.params}"
                    )
                    return f"@{message.params} is already chatting with another user"

                # if online and not chatting

                peer_1.socket.transmit()

                return None

            case _:  # How did you even get here dawg
                # send client error response
                StdoutLogger.log("NO TAMPERING ALLOWED")


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
