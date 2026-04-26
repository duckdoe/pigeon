from dataclasses import dataclass
from typing import Literal

ValueType = Literal['number', 'null', 'string', 'boolean']

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