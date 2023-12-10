""" Types for type assertion and generics """

from typing import Callable, TypeAlias, TypeVar


T = TypeVar("T")

# type Address = tuple[str, int]

Address: TypeAlias = tuple[str, int]

certain_attribute = Callable[[T], T]


# hello
