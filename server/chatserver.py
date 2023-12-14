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
        self.__database: Database = Database()

    def run(self) -> None:
        self.socket.bind()
        self.socket.listen()

        return_message: str | None = None

        """
        IMPORTANT! Link own socket to socket and plug. This is necessary when using the select.select function, because that function needs to be able to read the server socket as well.
        """
        self.link_socket_and_plug(self.get_socket(), self)

        print("~==========================================================~")
        print(f"\tyappin' chat server\t@{self.config.BINDING}")
        print("~==========================================================~")
        StdoutLogger.log(f"Server started...")

        try:
            while True:
                sockets: list[socket.socket] = self.all_primitive_sockets()
                read, _write, _error = select.select(sockets, [], [])

                for sock in read:
                    if sock is self.get_socket():
                        """
                        In this case, a new client wants to connect. Check if their connection is valid. If so, let them in and make a new user. If not, they are not allowed to connect. Delete their socket. Send a transmitted message back. NEW CLIENTS ARE ALWAYS A LOGIN REQUEST!
                        """
                        self._handle_incoming_connection(sock)

                    else:
                        """
                        Handle activity from other sockets, for example, those sockets may be sending messages to another socket.
                        """
                        self._handle_client_message(sock, return_message)

        except KeyboardInterrupt:
            # Close all sockets
            pass
        except Exception as e:
            print(f"An error has occurred: {e}")
            traceback.print_exc()
        finally:
            self.socket.close()

    def _handle_incoming_connection(self, sock: socket.socket) -> None:
        """
        Handles an incoming connection from an arbitrary client.
        """

        new_socket: socket.socket
        incoming_address: Address

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

        # turn the raw data from the socket into a usable message object
        raw_data = receive(new_socket)
        message = deserialize(raw_data)

        new_peer = ChatPeer(
            Config(provided_socket=new_client.get(), socket_blocking=False),
            username=message.sender,
            key=message.pubkey,
        )

        # creates a new ChatPeer from the new_client if username is valid
        # initializes peer in internal databases
        self._initialize_peer(new_peer)

        response = build_server_response(
            res_code=0,
            comment="have a nice stay",
            params=f"Online users: {self.connected_peers()}",
        )
        new_peer.send_data(response)

        StdoutLogger.user_action(new_peer.username, ACTIONS[message.action])
        StdoutLogger.log(f"currently online: {self.connected_peers()}")

        # validate the connection and make sure there is no duplicate username

    def _handle_client_message(
        self, sock: socket.socket, return_message: str | None
    ) -> None:
        # retrieve the ChatPeer object, given a socket
        connection: ChatPeer = self.socket_to_plug[sock]

        # read the data out of the connection (the socket)
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

    def _is_seated(self, username: str) -> bool:
        """Checks if a bozo is sitting at any table"""
        for table in self.__tables:
            if username in table.get_seated_info():
                return True

        return False

    def _initialize_peer(self, peer: ChatPeer) -> None:
        """
        Initializes internal connections for internal dictionaries.
        """
        self.link_socket_and_plug(peer.get_socket(), peer)
        self.link_id_and_peer(peer.username, peer)
        self.__database.store(peer)

    def data_handler(self, message: DataMessage, connection: ChatPeer) -> str | None:
        """
        Handles messages to the server. Incoming data bytes SHOULD BE ALREADY deserialized when being consumed by this function. The string returned from this method is information about an error, if there are any that occur. It is sent to the client.
        """

        # indicates whether an operation succeeded or not

        def _disconnect(peer_1: ChatPeer) -> None:
            """
            Disconnect from table, they no longer want to chat with each other.
            """

            peer_2_username: str

            for t in self.__tables:
                if peer_1.username in t.get_seated_info():
                    peer_2_username = t.get_peer(peer_1.username)
                    del t  # might break sh!t
                    break

            peer_2: ChatPeer = self.peer_from_id(peer_2_username)
            peer_2.set_state(State.CONNECTED)

            response = build_server_response(
                res_code=3, comment=f"{message.sender} has left the chat"
            )

            peer_2.send_data(response)

        StdoutLogger.user_action(message.sender, ACTIONS[message.action])

        # read the action
        match message.action:
            # LOGOUT
            case 1:  # I don't know why I can't use Action
                """
                Client full system logout.
                """
                sender = message.sender
                peer_1: ChatPeer = self.peer_from_id(sender)

                if peer_1.get_state() == State.CHATTING:
                    _disconnect(peer_1)

                # delete internal network associations and connections
                final = self.remove_connections(connection)

                # finally, close the socket for good
                final.socket.close()

                del final  # maybe add this?

                # internal database cleanup
                self.__database.set_user_state(sender, State.OFFLINE)

                return None

            # CONNECT
            case 2:
                """
                Connect one peer to another
                """
                sender = message.sender
                table: Table = Table()

                peer_1: ChatPeer = self.peer_from_id(sender)
                peer_2: ChatPeer

                peer_id = message.params

                """
                First, check if the "other user" is yourself. You cannot chat with yourself.
                """
                if peer_id == sender:
                    return f"you cannot chat with yourself"

                """
                Second, check if the other user is even online
                """
                if peer_id not in self.connected_peers():
                    return f"@{peer_id} is not online or does not exist"
                else:
                    # the message that peer sends to connect has params field containing the username of the connectee.
                    peer_2 = self.peer_from_id(peer_id)

                """
                Now check if the other user is engaged with someone else
                """
                if peer_2.get_state() is State.CHATTING:
                    StdoutLogger.log(
                        f"@{sender} attempted connection to CHATTING user @{sender}"
                    )
                    return f"@{sender} is already chatting with another user"

                """
                If both of the above conditions do not raise an error, continue with handshake
                """

                table.seat(peer_1)
                table.seat(peer_2)

                peer_2_key = build_server_response(
                    res_code=5,
                    pub_key=peer_2.Key,
                    params=peer_2.username,
                    comment="peer_2 key",
                )

                peer_1.send_data(peer_2_key)

                peer_1_key_res = build_server_response(
                    res_code=0,
                    comment="key handshake",
                    pub_key=peer_1.Key,
                    params=peer_1.username,
                )

                peer_2.send_data(peer_1_key_res)

                peer_1.set_state(State.CHATTING)
                peer_2.set_state(State.CHATTING)

                self.__tables.append(table)

                return None

            # DISCONNECT
            case 3:
                sender = message.sender
                peer_1: ChatPeer = self.peer_from_id(sender)

                # If bozo is chatting, they no longer are
                if peer_1.get_state() == State.CHATTING:
                    peer_1.set_state(State.CONNECTED)
                else:
                    return f"unable to leave: you are not chatting with anyone"

                # make their chat partner also no longer chatting
                _disconnect(peer_1)

                return None

            # MESSAGE
            case 5:
                sender = message.sender
                """
                Forwards a message to a recipient given the message object.
                """
                recipient_name = message.messages[0].receiver
                recipient: ChatPeer = self.peer_from_id(recipient_name)

                # serialize the data again because we had to deserialize it first to see the message's contents.
                data = serialize(message)

                # send the data to the recipient!
                recipient.send_data(data)

                return None

            case _:  # How did you even get here dawg
                # send client error response
                StdoutLogger.log("NO TAMPERING ALLOWED")
