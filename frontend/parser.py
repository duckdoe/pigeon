# TODO: Implement Call expressions
# TODO: Implement native function calls
# TODO: Implement println function for most types
# TODO: Implement arrays/list <- i dont know what to call them
# TODO: Implement comments and maybe multiine strings? <- Still a maybe

from typing import List

from . import asts
from .tokens import Token, TokenType


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.__body = []

    def generate_ast(self) -> asts.Program:
        while self.__not_eof():
            self.__body.append(self.__parse_stmt())

        return asts.Program("Program", self.__body)

    def __not_eof(self):
        return self.__cur_token().type != TokenType.Eof

    def __eat_token(self) -> Token:
        return self.tokens.pop(0)

    def __cur_token(self):
        return self.tokens[0]

    def __parse_stmt(self) -> asts.Stmt:
        match self.__cur_token().type:
            case TokenType.Let | TokenType.Const:
                return self.__parse_var_declaration_stmt()
            case TokenType.If:
                return self.__parse_if_statement()
            case _:
                return self.__parse_expr()

    def __parse_if_statement(self) -> asts.IfStatment:
        self.__eat_token()  # eat 'if' token

        condition = self.__parse_expr()

        if self.__eat_token().type != TokenType.LBrace:
            raise SyntaxError(
                "Unexpected token recieved, expected '{'"
                + f"got {self.__cur_token().type} at [ln: {self.__cur_token().ln}]"
            )

        body = []
        while self.__not_eof and self.__cur_token().type != TokenType.RBrace:
            body.append(self.__parse_stmt())

        if self.__eat_token().type != TokenType.RBrace:
            raise SyntaxError(
                "Unexepected end of file, expected '}'" + f" at {self.__cur_token().ln}"
            )

        branch = None

        if self.__cur_token().type == TokenType.Else and self.__peek_token(
            TokenType.If
        ):
            self.__eat_token()  # eat the 'else' token

            branch = self.__parse_if_statement()

            return asts.IfStatment("IfStatement", condition, body, branch)

        elif self.__cur_token().type == TokenType.Else and not self.__peek_token(
            TokenType.If
        ):
            self.__eat_token()  # eat 'else' token

            branch_body = []
            if self.__eat_token().type != TokenType.LBrace:
                raise SyntaxError(
                    "Unexpected token recieved, expected '{'"
                    + f"got {self.__cur_token().type} at [ln: {self.__cur_token().ln}]"
                )

            while self.__not_eof and self.__cur_token().type != TokenType.RBrace:
                branch_body.append(self.__parse_stmt())

            if self.__eat_token().type != TokenType.RBrace:
                raise SyntaxError(
                    "Unexepected end of file, expected '}'"
                    + f" at {self.__cur_token().ln}"
                )

            return asts.IfStatment(
                "IfStatement",
                condition,
                body,
                asts.ElseStatement("ElseStatement", branch_body),
            )

        return asts.IfStatment("IfStatement", condition, body, branch)

    def __peek_token(self, tokentype: TokenType) -> bool:
        if self.__not_eof():
            return self.tokens[1].type == tokentype

        return False

    def __parse_var_declaration_stmt(self) -> asts.VarDeclaration:
        var_type = self.__eat_token().value

        if self.__cur_token().type != TokenType.Ident:
            raise SyntaxError(
                f"Unexpected token recieved, expected an identifier got {self.__cur_token().type} at [ln: {self.__cur_token().ln}]"
            )

        name = self.__eat_token()

        if self.__cur_token().type != TokenType.Assign:
            raise SyntaxError(
                f"Unexpected token recieved, expected '=' got '{self.__cur_token().value}' at [ln: {self.__cur_token().ln}]"
            )

        self.__eat_token()  # Eat the '=' token

        value = self.__parse_expr()
        is_constant = True if var_type == "const" else False
        return asts.VarDeclaration("VarDeclaration", name, value, is_constant)

    def __parse_expr(self) -> asts.Expr:
        return self.__parse_assignment_expr()

    def __parse_assignment_expr(self) -> asts.Expr:
        lhs = self.__parse_or_expr()

        if lhs.kind == "Identifier" and self.__cur_token().type == TokenType.Assign:
            self.__eat_token()  # eat '=' token

            rhs = self.__parse_expr()

            return asts.AssignmentExpr("AssignmentExpr", lhs.symbol, rhs)  # type: ignore

        return lhs

    def __parse_or_expr(self) -> asts.Expr:

        left = self.__parse_and_expr()

        while self.__cur_token().value == "and":
            operator = self.__eat_token()
            right = self.__parse_and_expr()

            left = asts.BinaryExpr("BinExpr", left, operator, right)

        return left

    def __parse_and_expr(self) -> asts.Expr:
        left = self.__parse_comparison_expr()

        while self.__cur_token().value == "or":
            operator = self.__eat_token()
            right = self.__parse_comparison_expr()

            left = asts.BinaryExpr("BinExpr", left, operator, right)

        return left

    def __parse_comparison_expr(self) -> asts.Expr:
        left = self.__parse_comparison_arithmetic_expr()

        while self.__cur_token().value in ("==", "!="):
            operator = self.__eat_token()

            right = self.__parse_comparison_arithmetic_expr()

            left = asts.BinaryExpr("BinExpr", left, operator, right)

        return left

    def __parse_comparison_arithmetic_expr(self) -> asts.Expr:
        left = self.__parse_additve_expr()

        while self.__cur_token().value in (">", "<", "<=", ">="):
            operator = self.__eat_token()

            right = self.__parse_additve_expr()

            left = asts.BinaryExpr("BinExpr", left, operator, right)

        return left

    def __parse_additve_expr(self) -> asts.Expr:
        left = self.__parse_multiplicitive_expr()

        while self.__cur_token().value in ("-", "+"):
            operator = self.__eat_token()

            right = self.__parse_multiplicitive_expr()

            left = asts.BinaryExpr("BinExpr", left, operator, right)

        return left

    def __parse_multiplicitive_expr(self) -> asts.Expr:
        left = self.__parse_unary_expr()

        while self.__cur_token().value in ("/", "*", "%"):
            operator = self.__eat_token()

            right = self.__parse_unary_expr()

            left = asts.BinaryExpr("BinExpr", left, operator, right)

        return left

    def __parse_unary_expr(self) -> asts.Expr:
        if self.__cur_token().value in ("-", "+", "!"):
            return asts.UnaryExpr(
                "UnaryExpr",
                self.__eat_token(),
                self.__parse_call_expr(),
            )

        return self.__parse_call_expr()

    def __parse_call_expr(self) -> asts.Expr:
        caller = self.__parse_primary(self.__eat_token())
        args = None

        if self.__cur_token().type == TokenType.Lparen:
            self.__eat_token()
            args = self.__parse_args()

            caller = asts.CallExpr("CallExpr", caller, args)

        return caller

    def __parse_args(self) -> List[asts.Expr]:
        args = [self.__parse_expr()]

        while (
            self.__cur_token().type == TokenType.Comma
            and self.__cur_token().type != TokenType.Rparen
        ):
            self.__eat_token()
            args.append(self.__parse_expr())

        if self.__cur_token().type != TokenType.Rparen:
            raise SyntaxError(
                f"Unclosed parethesis during function call at [ln: {self.__cur_token().ln}]"
            )

        self.__eat_token()  # eats ')' token

        return args

    def __parse_primary(self, token: Token) -> asts.Expr:
        match token.type:
            case TokenType.Ident:
                return asts.Identifier("Identifier", token)
            case TokenType.String:
                return asts.StringLiteral("StringLiteral", token.value)
            case TokenType.Number:
                return asts.NumericLiteral("NumericLiteral", float(token.value))

            case TokenType.Lparen:
                value = self.__parse_expr()

                if self.__cur_token().type != TokenType.Rparen:
                    raise SyntaxError(
                        f"Unexpected token recieved, expected ')' got '{token.value}' at [ln: {token.ln}]"
                    )

                self.__eat_token()
                return value
            case TokenType.Bool:
                return asts.BooleanLiteral("BooleanLiteral", token.value)
            case TokenType.Null:
                return asts.NullLiteral("NullLiteral", token.value)
            case _:
                raise SyntaxError(
                    f"Unexpected token recieved, got '{token.value}' at [ln: {token.ln}]"
                )
