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
        return self.__parse_expr()

    def __parse_expr(self) -> asts.Expr:
        return self.__parse_comparison_expr()

    def __parse_comparison_expr(self) -> asts.Expr:
        left = self.__parse_additve_expr()

        while self.__cur_token().value in (">", "<", "==", "<=", ">="):
            operator = self.__eat_token().value

            right = self.__parse_additve_expr()

            left = asts.BinaryExpr("BinExpr", left, operator, right)

        return left

    def __parse_additve_expr(self) -> asts.Expr:
        left = self.__parse_multiplicitive_expr()

        while self.__cur_token().value in ("-", "+"):
            operator = self.__eat_token().value

            right = self.__parse_multiplicitive_expr()

            left = asts.BinaryExpr("BinExpr", left, operator, right)

        return left

    def __parse_multiplicitive_expr(self) -> asts.Expr:
        left = self.__parse_unary_expr()

        while self.__cur_token().value in ("/", "*", "%"):
            operator = self.__eat_token().value

            right = self.__parse_unary_expr()

            left = asts.BinaryExpr("BinExpr", left, operator, right)

        return left

    def __parse_unary_expr(self) -> asts.Expr:
        if self.__cur_token().value in ("-", "+", "!"):
            return asts.UnaryExpr(
                "UnaryExpr",
                self.__eat_token().value,
                self.__parse_primary(self.__eat_token()),
            )

        return self.__parse_primary(self.__eat_token())

    def __parse_primary(self, token: Token) -> asts.Expr:
        match token.type:
            case TokenType.Ident:
                return asts.Identifier("Identifier", token.value)
            case TokenType.String:
                return asts.StringLiteral("StringLiteral", token.value)
            case TokenType.Number:
                return asts.NumericLiteral("NumericLiteral", float(token.value))

            case TokenType.Lparen:
                value = self.__parse_expr()

                if self.__cur_token().type != TokenType.Rparen:
                    raise Exception(f"Syntax Error got {self.__cur_token()}")

                self.__eat_token()
                return value
            case TokenType.Bool:
                return asts.BooleanLiteral("BooleanLiteral", token.value)
            case TokenType.Null:
                return asts.NullLiteral("NullLiteral", token.value)
            case _:
                raise Exception(f"Syntax Error {token}")
