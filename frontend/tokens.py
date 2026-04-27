from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    If = auto()
    Or = auto()
    And = auto()
    Let = auto()
    Eof = auto()
    Null = auto()
    Bang = auto()
    Bool = auto()
    Else = auto()
    Comma = auto()
    Const = auto()
    BinOp = auto()
    Ident = auto()
    NotEq = auto()
    Lparen = auto()  # (
    Rparen = auto()  # )
    LBrace = auto()  # {
    RBrace = auto()  # }
    Number = auto()
    String = auto()
    Assign = auto()
    Equals = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    ln: int  # It means line dumbass


keywords = {
    "true": TokenType.Bool,
    "false": TokenType.Bool,
    "null": TokenType.Null,
    "or": TokenType.Or,
    "and": TokenType.And,
    "let": TokenType.Let,
    "const": TokenType.Const,
    "if": TokenType.If,
    "else": TokenType.Else,
}
