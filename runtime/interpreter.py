from errors import IllegalBreakError, IllegalContinueError
from frontend.asts import (
    AssignmentExpr,
    BinaryExpr,
    Identifier,
    MemberExpr,
    Program,
    Stmt,
    Token,
    UnaryExpr,
)

from .environment import Environment
from .values import Array, Boolean, Null, Number, RuntimeValue, String


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
            and node.operator.value in ("-", "*", "+", "/", "%")
        ):
            return self.__eval_arithmetic(left, right, node.operator)
        elif (
            left.type == "number"
            and right.type == "number"
            and node.operator.value in (">", "<", ">=", "<=")
        ):
            return self.__eval_arithmetic_comparison(left, right, node.operator)
        elif node.operator.value in ("==", "!="):
            return self.__eval_comparison_expr(left, right, node.operator)
        elif node.operator.value == "and":
            return self.__eval_short_circuit_and_expr(left, right, node.operator.ln)
        elif node.operator.value == "or":
            return self.__eval_short_circuit_or_expr(left, right, node.operator.ln)

        raise TypeError(
            f"cannot perform '{node.operator}' on type '{left.type}' and '{right.type}' at [ln: {node.operator.ln}]"
        )

    def __eval_short_circuit_and_expr(self, left, right, ln) -> Boolean:
        if left.type != "boolean" or right.type != "boolean":
            raise TypeError(
                f"Can only perform 'and' operations on boolean values [ln: {ln}]"
            )

        result = int(
            left.value == "true"
            and left.type == "boolean"
            and right.value == "true"
            and right.type == "boolean"
        )
        booleans = ["false", "true"]
        return Boolean("boolean", booleans[result])

    def __eval_short_circuit_or_expr(self, left, right, ln) -> Boolean:
        if left.type != "boolean" or right.type != "boolean":
            raise Exception(
                f"Can only perform 'and' operations on boolean values [ln: {ln}]"
            )

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

    def __eval_comparison_expr(self, left, right, operator: Token) -> Boolean:
        booleans = ["false", "true"]

        result = int(left.type == right.type and left.value == right.value)

        if operator.value == "!=":
            result -= 1  # This basically just flips the value

        return Boolean("boolean", booleans[result])

    def __eval_arithmetic_comparison(
        self, left: RuntimeValue, right: RuntimeValue, operator: Token
    ) -> Boolean:
        booleans = ["false", "true"]

        if operator.value == ">":
            result = booleans[int(left.value > right.value)]  # type: ignore
        elif operator.value == "<":
            result = booleans[int(left.value < right.value)]  # type: ignore
        elif operator.value == ">=":
            result = booleans[int(left.value >= right.value)]  # type: ignore
        else:
            result = booleans[int(left.value <= right.value)]  # type: ignore

        return Boolean("boolean", result)

    def __eval_arithmetic(
        self, left: RuntimeValue, right: RuntimeValue, operator: Token
    ) -> Number:
        if operator.value == "+":
            result = left.value + right.value  # type: ignore
        elif operator.value == "-":
            result = left.value - right.value  # type: ignore
        elif operator.value == "*":
            result = left.value * right.value  # type: ignore
        elif operator.value == "/":
            result = left.value / right.value  # type: ignore
        else:
            result = left.value % right.value  # type: ignore

        return Number("number", result)

    def __eval_unary_expr(self, node: UnaryExpr, env):
        operator = node.operator
        value = self.__evaluate_node(node.value, env)
        booleans = ["true", "false"]

        if operator.value == "-" and value.type == "number":
            return Number("number", value.value * -1)  # type: ignore
        elif operator.value == "+" and value.type == "number":
            return Number("number", value.value * 1)  # type: ignore
        elif operator.value == "!" and value.type == "boolean":
            return Boolean("boolean", booleans[booleans.index(value.value) - 1])  # type: ignore

        raise Exception(
            f"Type Error: Cannot perform '{operator}' on type '{value.type}'"
        )

    def __eval_identifier(self, node: Identifier, env: Environment) -> RuntimeValue:
        env = env.resolve(node.symbol.value)
        return env.look_up_var(node.symbol.value)

    def __eval_var_declaration(self, node, env: Environment) -> Null:
        value = self.__evaluate_node(node.value, env)
        env.declare_var(node.symbol.value, value, node.is_constant)

        return Null("null")

    def __eval_var_assignment(
        self, node: AssignmentExpr, env: Environment
    ) -> RuntimeValue:
        value = self.__evaluate_node(node.value, env)
        if node.symbol.value in env.constants:
            raise TypeError(
                f"Cannot reassign constant variable {node.symbol.value} at [ln: {node.symbol.ln}]"
            )

        env.assign_var(node.symbol.value, value)
        return value

    def __eval_if_statement(self, node, env: Environment) -> RuntimeValue:
        true = self.__evaluate_node(node.condition, env)

        if true.type != "boolean":
            raise TypeError(
                "Conditions in if statements can only be boolean data types"
            )
        elif true.type == "boolean" and true.value == "true":  # type: ignore
            for node in node.body:
                self.__evaluate_node(node, env)

            return Null("null")
        else:
            if node.branch is None:
                return Null("null")
            elif node.branch.kind == "IfStatement":
                self.__evaluate_node(node.branch, env)
            elif node.branch.kind == "ElseStatement":
                for node in node.branch.body:
                    self.__evaluate_node(node, env)

            return Null("null")

    def __eval_call_expr(self, node, env: Environment):
        fn = self.__evaluate_node(node.caller, env)
        args = [self.__evaluate_node(arg, env) for arg in node.args]

        return fn.call(args)  # type: ignore # this only works for native functions for now

    def __eval_member_expr(self, node: MemberExpr, env: Environment) -> RuntimeValue:
        if node.computed:
            object = self.__evaluate_node(node.object, env)
            property = self.__evaluate_node(node.property, env)

            if property.type == "number" and object.type == "array":
                return self.__eval_array_member(object, property)
            else:
                raise TypeError(
                    f"Cannot perform member call on object of type '{object.type}"
                )
        else:
            return Null(
                "null"
            )  # I have no idea why this is here but i think i need it.

    def __eval_array_member(self, object, property):
        remainder = property.value % 1

        if remainder != 0:
            raise TypeError(
                f"Array Indices must be an imterger value like '1' or '0' not {property.value}"
            )

        if len(object.value) < int(property.value):
            raise IndexError("Array index out of range")

        return object.value[int(property.value)]

    def __eval_while_stmt(self, node, env: Environment) -> RuntimeValue:
        # print(self.__evaluate_node(node.condition, env))
        while self.__evaluate_node(node.condition, env).value == "true": # type: ignore
            stop = False
            for n in node.body:
                try:
                    self.__evaluate_node(n, env)
                except IllegalBreakError:
                    stop = True
                    break
                except IllegalContinueError:
                    break  # This breaks out of the evaluating loop so we don't evaluate anymore nodes in the body, and just move straight back into evaluating the condition and then moving on with evaluating the body, I hope this works

            if stop is True:
                break

        return Null("null")

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
                return self.__eval_var_assignment(node, env)  # type: ignore
            case "IfStatement":
                return self.__eval_if_statement(node, env)
            case "CallExpr":
                return self.__eval_call_expr(node, env)
            case "ArrayLiteral":
                return Array(
                    "array",
                    [self.__evaluate_node(value, env) for value in node.properties],  # type: ignore
                )
            case "MemberExpr":
                return self.__eval_member_expr(node, env)  # type: ignore
            case "BreakStmt":
                raise IllegalBreakError("Illegal 'break' statement found")
            case "ContinueStmt":
                raise IllegalContinueError("Illegal 'continue' statement found")
            case "WhileStmt":
                return self.__eval_while_stmt(node, env)
            case _:
                raise Exception(f"Unexpected Error while evaluating {node}")
