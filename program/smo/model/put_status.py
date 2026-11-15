from enum import Enum, auto


class PutStatus(Enum):
    STORED = auto()
    EVICTED = auto()
