"""
This file creates a protobuf interface, wraps them.
"""


class ProtobufUserMessage:
    def __init__(self) -> None:
        self.sender: str
        self.receiver: str
        self.body: str
        self.date: int


class ProtobufUserMessages:
    def __init__(self, messages: list) -> None:
        self.messages: list[ProtobufUserMessage] = messages


class ProtobufAction:
    def __init__(self) -> None:
        pass


class ProtobufServerResponse:
    def __init__(self) -> None:
        pass
