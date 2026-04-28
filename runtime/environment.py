class Environment:
    def __init__(self, parent=None):
        self.parent: Environment | None = parent
        self.variables = {}
        self.constants = set()

    def resolve(self, key):
        if key in self.variables:
            return self

        if self.parent is None:
            raise Exception(f"Cannot resolve variable '{key}' as it does not exist")

        return self.parent.resolve(key)

    def look_up_var(self, key):
        env = self.resolve(key)

        return env.variables[key]

    def assign_var(self, key, value):
        if key not in self.variables:
            raise Exception(f"Cannot assign variable '{key}' as it does not exist yet")

        self.variables[key] = value

    def declare_var(self, key, value, constant: bool):
        if constant:
            self.constants.add(key)

        if key in self.variables:
            raise Exception(f"Cannot declare variable '{key}' as it already exists")
        self.variables[key] = value
