"""

How many errors do we need to implement? I think just syntax errors should be fine

"""


class Error:
    pass


class SyntaxError(Error):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self) -> str:
        return f"[Syntax Error]: {self.msg}"


class TypeError(Error):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self) -> str:
        return f"[Type Error]: {self.msg}"


class DivideByZeroError(Error):
    def __init__(self, mgs):
        self.msg = self.msg

    def __repr__(self) -> str:
        return f"[DivideByZero Error] {self.msg}"
