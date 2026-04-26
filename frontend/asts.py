from dataclasses import dataclass
from typing import List, Literal

NodeType = Literal[
    "BinExpr",
    "NumericLiteral",
    "StringLiteral",
    "Identifier",
    "UnaryExpr",
    "Program",
    "BooleanLiteral",
    "NullLiteral",
    "VarDeclaration",
]


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
class VarDeclaration(Stmt):
    symbol: str
    value: Expr
    is_constant: bool

@dataclass
class AssignmentExpr(Expr):
    symbol: str
    value: Expr


@dataclass
class NumericLiteral(Expr):
    value: float


@dataclass
class StringLiteral(Expr):
    value: str


@dataclass
class BooleanLiteral(Expr):
    value: str


@dataclass
class NullLiteral(Expr):
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
