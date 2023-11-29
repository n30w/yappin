""" Types for type assertion and generics """

from typing import Callable, TypeVar


T = TypeVar("T")

Address = TypeVar("Address", tuple[str, int])

certain_attribute = Callable[[T], T]

# hello 