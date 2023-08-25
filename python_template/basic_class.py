from dataclasses import dataclass
from typing import Protocol


@dataclass
class BasicClass:
    int_var: int = 0


class BasicProtocol(Protocol):
    def method(self):
        ...
