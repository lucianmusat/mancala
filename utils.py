from enum import Enum


class MoveResult(Enum):
    Invalid = -1
    InOwnBigPit = 0
    Valid = 1
