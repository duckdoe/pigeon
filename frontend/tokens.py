from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    Or = auto()
    And = auto()
    Let = auto()
    Eof = auto()
    Null = auto()
    Bang = auto()
    Bool = auto()
    Const = auto()
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


keywords = {
    "true": TokenType.Bool,
    "false": TokenType.Bool,
    "null": TokenType.Null,
    "or": TokenType.Or,
    "and": TokenType.And,
    "let": TokenType.Let,
    "const": TokenType.Const,
}
