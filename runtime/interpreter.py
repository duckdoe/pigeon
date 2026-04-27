from frontend.asts import BinaryExpr, Identifier, Program, Stmt, UnaryExpr

from .environment import Environment
from .values import Boolean, Null, Number, RuntimeValue, String


class Intpereter:
    def __init__(self, program: Program) -> None:
        self.program = program

    def eval(self, env) -> RuntimeValue:
        return self.__evaluate_node(self.program, env)

    def __eval_program(self, env: Environment) -> RuntimeValue:
        last_evaluated = Null("null")

        for node in self.program.body:
            last_evaluated = self.__evaluate_node(node, env)

        return last_evaluated

    def __eval_binary_expr(self, node: BinaryExpr, env: Environment) -> RuntimeValue:
        left = self.__evaluate_node(node.left, env)
        right = self.__evaluate_node(node.right, env)

        if (
            left.type == "number"
            and right.type == "number"
            and node.operator in ("-", "*", "+", "/", "%")
        ):
            return self.__eval_arithmetic(left, right, node.operator)
        elif (
            left.type == "number"
            and right.type == "number"
            and node.operator in (">", "<", ">=", "<=")
        ):
            return self.__eval_arithmetic_comparison(left, right, node.operator)
        elif node.operator == "==":
            return self.__eval_comparison_expr(left, right)
        elif node.operator == "and":
            return self.__eval_short_circuit_and_expr(left, right)
        elif node.operator == "or":
            return self.__eval_short_circuit_or_expr(left, right)

        raise Exception(
            f"TypeError, cannot perform '{node.operator}' on type '{left.type}' and '{right.type}'"
        )

    def __eval_short_circuit_and_expr(self, left, right) -> Boolean:
        if left.type != "boolean" or right.type != "boolean":
            raise Exception("Can only perform 'and' operations on boolean values")

        result = int(
            left.value == "true"
            and left.type == "boolean"
            and right.value == "true"
            and right.type == "boolean"
        )
        booleans = ["false", "true"]
        return Boolean("boolean", booleans[result])

    def __eval_short_circuit_or_expr(self, left, right) -> Boolean:
        if left.type != "boolean" or right.type != "boolean":
            raise Exception("Can only perform 'or' operations on boolean values")

        if left.value == "true" and left.type == "boolean":
            return Boolean("boolean", "true")

        result = int(
            left.value == "false"
            and left.type == "boolean"
            or right.value == "true"
            and right.type == "boolean"
        )
        booleans = ["false", "true"]
        return Boolean("boolean", booleans[result])

    def __eval_comparison_expr(self, left, right) -> Boolean:
        booleans = ["false", "true"]
        result = int(left.type == right.type and left.value == right.value)

        return Boolean("boolean", booleans[result])

    def __eval_arithmetic_comparison(
        self, left: RuntimeValue, right: RuntimeValue, operator: str
    ) -> Boolean:
        booleans = ["false", "true"]

        if operator == ">":
            result = booleans[int(left.value > right.value)]  # type: ignore
        elif operator == "<":
            result = booleans[int(left.value < right.value)]  # type: ignore
        elif operator == ">=":
            result = booleans[int(left.value >= right.value)]  # type: ignore
        else:
            result = booleans[int(left.value <= right.value)]  # type: ignore

        return Boolean("boolean", result)

    def __eval_arithmetic(
        self, left: RuntimeValue, right: RuntimeValue, operator: str
    ) -> Number:
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

    def __eval_unary_expr(self, node: UnaryExpr, env):
        operator = node.operator
        value = self.__evaluate_node(node.value, env)
        booleans = ["true", "false"]

        if operator == "-" and value.type == "number":
            return Number("number", value.value * -1)  # type: ignore
        elif operator == "+" and value.type == "number":
            return Number("number", value.value * 1)  # type: ignore
        elif operator == "!" and value.type == "boolean":
            return Boolean("boolean", booleans[booleans.index(value.value) - 1])  # type: ignore

        raise Exception(
            f"Type Error: Cannot perform '{operator}' on type '{value.type}'"
        )

    def __eval_identifier(self, node: Identifier, env: Environment) -> RuntimeValue:
        env = env.resolve(node.symbol)
        return env.look_up_var(node.symbol)

    def __eval_var_declaration(self, node, env: Environment) -> Null:
        value = self.__evaluate_node(node.value, env)
        env.declare_var(node.symbol, value, node.is_constant)

        return Null("null")

    def __eval_var_assignment(self, node, env: Environment) -> RuntimeValue:
        value = self.__evaluate_node(node.value, env)

        env.assign_var(node.symbol, value)
        return value

    def __evaluate_node(self, node: Stmt, env: Environment) -> RuntimeValue:
        match node.kind:
            case "Program":
                return self.__eval_program(env)
            case "NullLiteral":
                return Null("null")
            case "NumericLiteral":
                return Number("number", node.value)  # type: ignore
            case "BooleanLiteral":
                return Boolean("boolean", node.value)  # type: ignore
            case "StringLiteral":
                return String("string", node.value)  # type: ignore
            case "BinExpr":
                return self.__eval_binary_expr(node, env)  # type: ignore
            case "UnaryExpr":
                return self.__eval_unary_expr(node, env)  # type: ignore
            case "Identifier":
                return self.__eval_identifier(node, env)  # type: ignore
            case "VarDeclaration":
                return self.__eval_var_declaration(node, env)
            case "AssignmentExpr":
                return self.__eval_var_assignment(node, env)
            case _:
                raise Exception(f"Unexpected Error while evaluating {node}")
