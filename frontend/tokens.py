from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    Eof = auto()
    Null = auto()
    Bang = auto()
    Bool = auto()
    BinOp = auto()
    Ident = auto()
    Lparen = auto()  # (
    Rparen = auto()  # )
    Number = auto()
    String = auto()
    Assign = auto()
    Equals = auto()


@dataclass
class Token:
    type: TokenType
    value: str


keywords = {"true": TokenType.Bool, "false": TokenType.Bool, "null": TokenType.Null}
