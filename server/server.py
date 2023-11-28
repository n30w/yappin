from server.net import Config
from server.peer import Peer
from shared.types import T


class Server:
    def __init__(self, config: Config) -> None:
        self.__config: Config = config
        self.__router: Router = Router()

    # New sockets from peers must be in non-blocking mode
    # socket.setblocking(0)
    # so the program does not halt while handling connections. Concurrent execution.

    def run(self) -> None:
        """
        TODO: Add socket logic and select statements.
        Note that select.select reads the sockets and returns them, in a list. That list has all of the sockets that the server can then operate on. For each item in the list, the server decides what to do with it given certain conditions.
        """
        pass


class Router:
    """
    Routes data between internal server components. Does NOT transmit anything via network connections, that is what net module is for. This is an internal server class.
    """

    def __init__(self) -> None:
        self.__selection: T = None

    def select(self, target: T) -> None:
        """
        Selects a target, i.e. the thing or the "what" that will be routed.
        """

        self.__selection = target

    def route_to(self, dest: T) -> None:
        """
        Routes an object to an internal destination. Returns a bool of whether the routing was possible or not.
        """

        dest.consume(self.__selection)
        self.__selection = None


# Servicer does all the high-level operations we want the server to do, for example kicking someone out. Basically business logic.
class Servicer:
    def __init__(self) -> None:
        pass


# Bookkeeper makes sure all data is logged and stored, and makes sure users are logged.
class Bookkeeper:
    def __init__(self) -> None:
        pass
