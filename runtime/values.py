from dataclasses import dataclass
from typing import Callable, List, Literal, Dict

from frontend.asts import Stmt, Identifier
from .environment import Environment

ValueType = Literal["number", "null", "string", "boolean", "nativefn", "array", "function", "map"]


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
class Map(RuntimeValue):
    properties: Dict[str, RuntimeValue]


@dataclass
class Function(RuntimeValue):
    declaration_env: Environment
    params: List[Identifier]
    call: List[Stmt]
