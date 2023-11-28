""" Types for type assertion and generics """

from typing import TypeVar


T = TypeVar("T")

Address = TypeVar("Address", tuple[str, int])
