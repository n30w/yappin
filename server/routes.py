def login() -> bool:
    """
    Route to login a user. Since logging in is the first thing that is sent during a client handshake, this function must check if the username is taken or not. This can deny connections.

    The bool returned determines its success. True if successful, false if not.
    """
    pass


def logout():
    """
    Disconnects the socket of the user, sets their status to OFFLINE.
    """
    pass


def connect():
    """
    Connects a user to another user.
    """
    pass


def disconnect():
    """
    disconnects a user from a conversation, removes them from a table.
    """
    pass


def search():
    """
    Searches the chats for related keywords.
    """
    pass


def message():
    """
    Sends a message to another user.
    """
    pass


def route_handler() -> bool:
    pass
