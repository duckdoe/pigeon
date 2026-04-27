from dataclasses import dataclass
from typing import Callable, Literal, List

ValueType = Literal["number", "null", "string", "boolean", "nativefn", "array"]


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