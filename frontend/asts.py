from dataclasses import dataclass
from typing import List, Literal

from .tokens import Token

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
    "AssignmentExpr",
    "IfStatement",
    "ElseStatement",
    "CallExpr",
    "ArrayLiteral",
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
    symbol: Token
    value: Expr
    is_constant: bool


@dataclass
class IfStatment(Stmt):
    condition: Expr
    body: List[Stmt]
    branch: (
        Stmt | None
    )  # If statements can exist independently without any branch such as 'else if' or 'else'


@dataclass
class ElseStatement(Stmt):
    body: List[Stmt]


@dataclass
class AssignmentExpr(Expr):
    symbol: Token
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
    symbol: Token


@dataclass
class BinaryExpr(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass
class UnaryExpr(Expr):
    operator: Token
    value: Expr


@dataclass
class CallExpr(Expr):
    caller: Expr
    args: (
        List[Expr] | None
    )  # variable declarations, if statements and function declarations cannot exist in arguments

@dataclass
class ArrayLiteral(Expr):
    properties: List[Expr]