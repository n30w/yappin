"""
This file contains classes and functions related to chatting.
"""

from peer import *


class Table:
    """
    A "Table" is where peers sit down and chat, like a physical coffee table in the nook of a cafe. Tables are limited to two people. Tables are where discussions (chats) are facilitated.

    ---

    ### Attributes
        @seats: dict[str, ChatPeer] -- a dict of Peer objects containing the two peers seated at the table.
        @created_time: str -- the time the table was instantiated.
        @key_ring: list[Key] -- a list of two keys that holds the two public keys of the peers.

    ### Methods
        is_vacant -- returns a bool of whether or not a table has guests seated.
    """

    def __init__(self) -> None:
        # str is username of peer
        self.seats: dict[str, ChatPeer] = {}
        self.created_time: str = ""  # IMPLEMENT TIME PACKAGE

    def is_vacant(self) -> bool:
        """
        Are there any patrons sitting at this table?
        """
        if len(self.seats) == 0:
            return True
        return False

    def get_seated_info(self) -> list[str]:
        """
        Returns the peers sitting at the table.
        """
        return self.seats.keys()

    def get_peer(self, of: str) -> str:
        for peer in self.seats.keys():
            if peer is not of:
                return peer

    def seat(self, peer: ChatPeer) -> bool:
        """
        seat "seats" guests at the table into their seats. Only two per table. Returns a bool that represents if seating was successful. Keep in mind here, seat is both a noun and a transitive verb in English. The method name here is the verb form. The infinitive verb form of "seat" is "to seat".
        """

        if len(self.seats) == 2:
            return False
        else:
            self.seats[peer.username] = peer
            return True
