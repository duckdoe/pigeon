from dataclasses import dataclass
from typing import Callable, List, Literal

from frontend.asts import Stmt, Identifier
from .environment import Environment

ValueType = Literal["number", "null", "string", "boolean", "nativefn", "array", "function"]


@dataclass
class RuntimeValue:
    type: ValueType


@dataclass
class Number(RuntimeValue):
    value: float


@dataclass
class String(RuntimeValue):
    value: str


@dataclass
class Boolean(RuntimeValue):
    value: str


@dataclass
class Null(RuntimeValue):
    value = "null"


@dataclass
class NativeFn(RuntimeValue):
    call: Callable


@dataclass
class Array(RuntimeValue):
    value: List[RuntimeValue]


@dataclass
class Function(RuntimeValue):
    declaration_env: Environment
    params: List[Identifier]
    call: List[Stmt]
