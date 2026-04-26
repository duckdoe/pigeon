from frontend.asts import BinaryExpr, Program, Stmt

from .values import Boolean, Null, Number, RuntimeValue, String


class Intpereter:
    def __init__(self, program: Program) -> None:
        self.program = program

    def eval(self) -> RuntimeValue:
        return self.__eval_program()

    def __eval_program(self) -> RuntimeValue:
        last_evaluated = Null("null")

        for node in self.program.body:
            last_evaluated = self.__evaluate_node(node)

        return last_evaluated

    def __eval_binary_expr(self, node: BinaryExpr) -> RuntimeValue:
        left = self.__evaluate_node(node.left)
        right = self.__evaluate_node(node.right)

        if left.type == "number" and right.type == "number":
            return self.__eval_arithmetic(left, right, node.operator)

        raise Exception(
            f"TypeError, cannot perform '{node.operator}' on type '{left.type}' and '{right.type}'"
        )

    def __eval_arithmetic(
        self, left: RuntimeValue, right: RuntimeValue, operator: str
    ) -> RuntimeValue:
        if operator == "+":
            result = left.value + right.value  # type: ignore
        elif operator == "-":
            result = left.value - right.value  # type: ignore
        elif operator == "*":
            result = left.value * right.value  # type: ignore
        elif operator == "/":
            result = left.value / right.value  # type: ignore
        else:
            result = left.value % right.value  # type: ignore

        return Number("number", result)

    def __evaluate_node(self, node: Stmt) -> RuntimeValue:
        match node.kind:
            case "Program":
                return self.__eval_program()
            case "NullLiteral":
                return Null("null")
            case "NumericLiteral":
                return Number("number", node.value)  # type: ignore
            case "BooleanLiteral":
                return Boolean("boolean", node.value)  # type: ignore
            case "StringLiteral":
                return String("string", node.value)  # type: ignore
            case "BinExpr":
                return self.__eval_binary_expr(node)  # type: ignore
            case _:
                raise Exception(f"Unexpected Error while evaluating {node}")
