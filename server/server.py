from server.peer import Peer
from server.net import Config


class Server:
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    # New sockets from peers must be in non-blocking mode
    # socket.setblocking(0)
    # so the program does not halt while handling connections. Concurrent execution.

    def run(self) -> None:
        """
        TODO: Add socket logic and select statements.
        Note that select.select reads the sockets and returns them, in a list. That list has all of the sockets that the server can then operate on. For each item in the list, the server decides what to do with it given certain conditions.
        """
        pass


# Networker establishes connections with peers and maintains connections.
class Networker:
    def __init__(self) -> None:
        pass


# Servicer does all the high-level operations we want the server to do, for example kicking someone out. Basically business logic.
class Servicer:
    def __init__(self) -> None:
        pass


# Messenger routes messages between peers.
class Messenger:
    def __init__(self) -> None:
        pass


# Bookkeeper makes sure all data is logged and stored, and makes sure users are logged.
class Bookkeeper:
    def __init__(self) -> None:
        pass


# A "Table" is where peers sit down and chat, like the nook of a cafe.
class Table:
    def __init__(self) -> None:
        # Seats contains the people seated at the table, the peers.
        self.seats: list[Peer] = []
        self.created_time: str = ""  # IMPLEMENT TIME PACKAGE

    # get_information returns information about who is at the table and things like that.
    def get_information(self) -> str:
        pass

    # seat "seats" guests at the table. Only two per table. Returns a bool that represents if seating was successful. Keep in mind here, seat is both a noun and a transitive verb in English. The method name here is the verb form.
    def seat(self, peer: Peer) -> bool:
        if len(self.seats) == 2:
            return False
        else:
            self.seats.append(peer)
            return True
