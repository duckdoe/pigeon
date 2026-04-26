from dataclasses import dataclass
from typing import Literal, List

NodeType = Literal["BinExpr", "NumericLiteral", "StringLiteral", "Identifier", "UnaryExpr", "Program"]

@dataclass
class Stmt:
    kind: NodeType

@dataclass
class Expr(Stmt):
    pass


@dataclass
class Program(Stmt):
    body: List[Stmt]

@dataclass
class NumericLiteral(Expr):
    value: float

@dataclass
class StringLiteral(Expr):
    value: str

@dataclass
class Identifier(Expr):
    symbol: str

@dataclass
class BinaryExpr(Expr):
    left: Expr
    operator: str
    right: Expr

@dataclass
class UnaryExpr(Expr):
    operator: str
    value: Expr