from typing import Self
from server.chat import Table
from server.net import Config
from server.peer import Peer
from shared.types import T


class Server:
    def __init__(self, config: Config) -> None:
        self.__config: Config = config
        self.__router: Router = Router()
        self.__bookkeeper: Bookkeeper = Bookkeeper()
        self.__tables: list[Table] = list()

    # New sockets from peers must be in non-blocking mode
    # socket.setblocking(0)
    # so the program does not halt while handling connections. Concurrent execution.

    def run(self) -> None:
        """
        TODO: Add socket logic and select statements.
        Note that select.select reads the sockets and returns them, in a list. That list has all of the sockets that the server can then operate on. For each item in the list, the server decides what to do with it given certain conditions.
        """
        pass

    # Will move this somewhere else later, maybe
    def key_handshake(self) -> None:
        """
        Exchange the keys between the peers at the table, after they are seated.
        """

        table: Table = Table()

        # Route key from the first peer to the second peer.
        self.__router.select(table.seats[0].get_key()).route_to(table.seats[1])

        # Route key from the second peer to the first peer
        self.__router.select(table.seats[1].get_key()).route_to(table.seats[0])


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


# Bookkeeper makes sure all data is logged and stored, and makes sure users are logged.
class Bookkeeper:
    def __init__(self) -> None:
        pass

    def tabulate_message(self) -> None:
        pass
