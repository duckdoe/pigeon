from typing import Dict

from .values import RuntimeValue


class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.variables: Dict[str, RuntimeValue] = {}

    def resolve(self, key):
        if key in self.variables:
            return self

        if self.parent is None:
            raise Exception(f"Cannot resolve variable '{key}' as it does not exist")

        return self.parent.resolve(key)

    def look_up_var(self, key) -> RuntimeValue:
        env = self.resolve(key)

        return env.variables[key]

    def assign_var(self, key, value: RuntimeValue):
        if key not in self.variables:
            raise Exception(f"Cannot assign variable '{key}' as it does not exist yet")

        self.variables.setdefault(key, value)

    def declare_var(self, key, value: RuntimeValue):
        self.variables.setdefault(key, value)
