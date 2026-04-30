from errors import IllegalBreakError, IllegalContinueError, IllegalReturnError
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
from .values import Array, Boolean, Function, Map, Null, Number, RuntimeValue, String


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
            left.type == "string"
            and right.type == "string"
            and node.operator.value == "+"
        ):
            return String("string", left.value + right.value)  # type: ignore
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

    def __eval_assignment_expr(self, node: AssignmentExpr, env: Environment):
        value = self.__evaluate_node(node.value, env)
        assignee: MemberExpr = node.symbol  # type: ignore

        if assignee.kind == "Identifier":
            if node.symbol.symbol.value in env.constants:  # type: ignore
                raise TypeError(
                    f"Cannot reassign constant variable {node.symbol.symbol.value} at [ln: {node.symbol.ln}]"  # type: ignore
                )
            env.assign_var(node.symbol.symbol.value, value)  # type: ignore
            return value

        elif assignee.kind == "MemberExpr":
            # first need to destructure the ast node into something we can transverse over to reasign values
            # we need the name of the member, meaning the one that binds the data structure

            """
            The ideal datastructure should be a tuple, so if we have something like this, name.age.first, we should get
            ('name', 'age', 'first'), where the first value is the variable
            """

            return_val = []

            while assignee.kind == "MemberExpr":
                return_val.append(
                    assignee.property.symbol.value  # type: ignore
                    if assignee.property.kind == "Identifier"
                    else assignee.property.value  # type: ignore
                )
                assignee = assignee.object  # type: ignore

            if assignee.kind == "NumericLiteral":
                return_val.append(assignee.value)  # type: ignore
            elif assignee.kind == "Identifier":
                return_val.append(assignee.symbol.value)  # type: ignore

            object = env.look_up_var(return_val.pop())

            if object.type == "map":
                while len(return_val) != 1:
                    key = return_val.pop()

                    if key not in object.properties:
                        raise TypeError(f"Object does not have property {key} at {assignee.property.symbol.ln}") # typeL ignore

                    object = object.properties.get(key)

                if object.type == "map":
                    object.properties[return_val.pop()] = value

                elif object.type == "array":
                    object.value[int(return_val.pop())] = value

                return value
            elif object.type == "array":
                while len(return_val) != 1:
                    key = return_val.pop()

                    if key > len(object.value):
                        raise TypeError(
                            f"IndexError {key.value} is beyond the lenght of the array [ln:]"
                        )

                    object = object.value[int(key)]

                if object.type == "map":
                    object.properties[return_val.pop()] = value

                elif object.type == "array":
                    object.value[int(return_val.pop())] = value

                return value
            else:
                raise TypeError(
                    f"Cannot assign '{object.type}' to right hand side value"
                )
        else:
            raise TypeError(f"Cannot assign '{object.type}' to right hand side value") # type: ignore

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

    def __eval_call_expr(self, node, env: Environment) -> RuntimeValue:
        fn = self.__evaluate_node(node.caller, env)
        args = [self.__evaluate_node(arg, env) for arg in node.args]

        if fn.type == "nativefn":
            return fn.call(args)  # type: ignore # this only works for native functions for now
        else:
            return self.__eval_function_call(args, fn)  # type: ignore

    def __eval_function_call(self, args, fn: Function) -> RuntimeValue:
        if len(args) != len(fn.params):
            raise TypeError(
                f"Expected {len(fn.params)} argumentss, got {len(fn.params)} instead"
            )

        for i in range(len(args)):
            fn.declaration_env.declare_var(fn.params[i].symbol.value, args[i], False)

        should_return = False

        for i in range(len(fn.call)):
            try:
                self.__evaluate_node(fn.call[i], fn.declaration_env)
            except IllegalReturnError as e:
                return_val = e.args[1]
                should_return = True
                break

        if should_return:
            return self.__evaluate_node(return_val.value, fn.declaration_env)  # type: ignore

        return Null("null")

    def __eval_member_expr(self, node: MemberExpr, env: Environment) -> RuntimeValue:
        if node.computed:
            object = self.__evaluate_node(node.object, env)
            property = self.__evaluate_node(node.property, env)

            if property.type == "number":
                if object.type == "array":
                    return self.__eval_array_member(object, property)
                elif object.type == "string":
                    remainder = property.value % 1  # type: ignore

                    if remainder != 0:
                        raise TypeError(
                            f"string indices must be an imterger value like '1' or '0' not {property.value}"  # type: ignore
                        )

                    return String("string", object.value[int(property.value)])  # type: ignore
            raise TypeError(
                f"value of type {object.type} is not subscriptable"  # type: ignore
            )
        else:
            object = self.__evaluate_node(node.object, env)

            if object.type != "map":
                raise TypeError(f"cannot perform dot notation on type {object.type}")

            if node.property.kind == "CallExpr":
                key = node.property.caller.symbol.value  # type: ignore

                if key not in object.properties:  # type: ignore
                    raise KeyError(
                        f"'{key}' does not exist as a property in {node.object}"
                    )

                fn = object.properties[key]  # type: ignore

                if fn.type != "function":
                    raise Exception(f"Cannot call '{key}' as it is not a function")

                return self.__eval_function_call(node.property.args, fn)  # type: ignore

            if node.property.kind != "Identifier":
                raise Exception("This is an error")

            property = node.property.symbol.value  # type: ignore

            return object.properties[property]  # type: ignore

    def __eval_array_member(self, object, property):
        remainder = property.value % 1

        if remainder != 0:
            raise TypeError(
                f"array Indices must be an imterger value like '1' or '0' not {property.value}"
            )

        if len(object.value) < int(property.value):
            raise IndexError("Array index out of range")

        return object.value[int(property.value)]

    def __eval_while_stmt(self, node, env: Environment) -> RuntimeValue:
        while self.__evaluate_node(node.condition, env).value == "true":  # type: ignore
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

    def __eval_for_stmt(self, node, scope: Environment) -> RuntimeValue:
        self.__evaluate_node(node.declaration, scope)

        condition = self.__evaluate_node(node.condition, scope)

        if condition.type != "boolean":
            raise TypeError("Condition must be of type boolean")

        while self.__evaluate_node(node.condition, scope).value == "true":  # type: ignore
            stop = False

            for n in node.body:
                try:
                    self.__evaluate_node(n, scope)
                except IllegalBreakError:
                    stop = True
                    break
                except IllegalContinueError:
                    break

            if stop is True:
                break

            self.__evaluate_node(node.action, scope)

        return Null("null")

    def __eval_function_declaration(self, node, env: Environment) -> RuntimeValue:
        name = node.symbol.symbol.value

        for param in node.params:
            if param.kind != "Identifier":
                raise SyntaxError(
                    "Function parameters can only be of type 'identifiers'"
                )

        fn = Function("function", env, node.params, node.body)
        env.parent.declare_var(name, fn, True)  # type: ignore
        return Null("null")

    def __eval_function_expr(self, node, env):
        for param in node.params:
            if param.kind != "Identifier":
                raise SyntaxError(
                    "Function parameters can only be of type 'identifiers'"
                )

        return Function("function", env, node.params, node.body)

    def __eval_object_expr(self, node, env: Environment) -> RuntimeValue:
        map = {}
        for property in node.properties:
            key = property.key.value

            if property.value is None:
                try:
                    value = env.look_up_var(key)
                except Exception:
                    value = Null("null")

                map.update({key: value})
                continue

            value = self.__evaluate_node(property.value, env)

            map.update({key: value})

        return Map("map", map)

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
                return self.__eval_assignment_expr(node, env)  # type: ignore
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
                raise IllegalBreakError("'break' statements can only exist in groups")
            case "ContinueStmt":
                raise IllegalContinueError(
                    "'continue' statements can only exist in loops"
                )
            case "WhileStmt":
                return self.__eval_while_stmt(node, env)
            case "ForStmt":
                scope = Environment(env)
                return self.__eval_for_stmt(node, scope)
            case "FunctionDeclaration":
                scope = Environment(env)
                return self.__eval_function_declaration(node, scope)
            case "ReturnStmt":
                raise IllegalReturnError(
                    "'return' statements can only exist in functions", node
                )
            case "FunctionExpr":
                scope = Environment(env)
                return self.__eval_function_expr(node, scope)
            case "MapLiteral":
                return self.__eval_object_expr(node, env)
            case _:
                raise Exception(f"Unexpected Error while evaluating {node}")
