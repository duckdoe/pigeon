from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    Eof    = auto()
    Bang   = auto()
    BinOp  = auto()
    Ident  = auto()
    Lparen = auto() # (
    Rparen = auto() # )
    Number = auto()
    String = auto()


@dataclass
class Token:
    type: TokenType
    value: str