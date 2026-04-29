from typing import List, Optional

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
            case TokenType.While:
                return self.__parse_while_stmt()
            case TokenType.Break:
                self.__eat_token()
                return asts.BreakStmt("BreakStmt")
            case TokenType.Continue:
                self.__eat_token()
                return asts.BreakStmt("ContinueStmt")
            case TokenType.For:
                return self.__parse_for_stmt()
            case TokenType.Fn:
                return self.__parse_function_declaration()
            case TokenType.Return:
                self.__eat_token()
                return asts.ReturnStmt("ReturnStmt", self.__parse_expr())
            case _:
                return self.__parse_expr()

    def __parse_function_declaration(self) -> asts.FunctionDeclaration:
        self.__eat_token()  # eat 'fn' token

        if self.__cur_token().type != TokenType.Ident:
            raise SyntaxError(
                f"Expected an identifier, got '{self.__cur_token().value}' instead"
            )

        symbol = self.__parse_primary(self.__eat_token())

        if self.__eat_token().type != TokenType.Lparen:
            raise SyntaxError(f"Expected '(' got '{self.__cur_token().value}' instead")

        params = self.__parse_args()

        if self.__eat_token().type != TokenType.LBrace:
            raise SyntaxError(
                "Expected '{' got" + f"'{self.__cur_token().value}' instead"
            )

        body = []
        while self.__cur_token().type != TokenType.RBrace and self.__not_eof():
            body.append(self.__parse_stmt())

        if self.__eat_token().type != TokenType.RBrace:
            raise SyntaxError(
                "Expected '}' got"
                + f"'{self.__cur_token().value}' instead at {self.__cur_token().ln}"
            )

        return asts.FunctionDeclaration("FunctionDeclaration", symbol, params, body)

    def __parse_for_stmt(self) -> asts.ForStmt:
        self.__eat_token()  # eat 'for' token
        declaration = self.__parse_var_declaration_stmt()

        if self.__eat_token().type != TokenType.SemiColon:
            raise SyntaxError(
                f"Unexpected token recieved, Expected ';' got '{self.__cur_token().value}'"
            )

        condition = self.__parse_expr()

        if self.__eat_token().type != TokenType.SemiColon:
            raise SyntaxError(
                f"Unexpected token recieved, Expected ';' got '{self.__cur_token().value}'"
            )

        action = self.__parse_expr()

        if self.__eat_token().type != TokenType.LBrace:
            raise SyntaxError(
                "Unexpected token recieved, Expected '{'"
                + f" got '{self.__cur_token().value}'"
            )

        body = []
        while self.__cur_token().type != TokenType.RBrace:
            body.append(self.__parse_stmt())

        if self.__eat_token().type != TokenType.RBrace:
            raise SyntaxError(
                "Unexpected token recieve, Expected '}'"
                + f" got '{self.__cur_token().value}'"
            )

        return asts.ForStmt("ForStmt", declaration, action, condition, body)

    def __parse_while_stmt(self) -> asts.Stmt:
        self.__eat_token()  # eat 'while' token
        condition = self.__parse_expr()

        if self.__eat_token().type != TokenType.LBrace:
            raise SyntaxError(
                "Unexpected token recieved, expected '{'"
                + f"got {self.__cur_token().type} at [ln: {self.__cur_token().ln}]"
            )

        body = []
        while self.__not_eof() and self.__cur_token().type != TokenType.RBrace:
            body.append(self.__parse_stmt())

        if self.__eat_token().type != TokenType.RBrace:
            raise SyntaxError(
                "Unexepected end of file, expected '}'" + f" at {self.__cur_token().ln}"
            )

        return asts.WhileStmt("WhileStmt", condition, body)

    def __parse_if_statement(self) -> asts.IfStatment:
        self.__eat_token()  # eat 'if' token

        condition = self.__parse_expr()

        if self.__eat_token().type != TokenType.LBrace:
            raise SyntaxError(
                "Unexpected token recieved, expected '{'"
                + f"got {self.__cur_token().type} at [ln: {self.__cur_token().ln}]"
            )

        body = []
        while self.__not_eof() and self.__cur_token().type != TokenType.RBrace:
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
        return self.__parse_function_expr()

    def __parse_function_expr(self) -> asts.Expr:
        if self.__cur_token().type != TokenType.Fn:
            return self.__parse_assignment_expr()

        self.__eat_token()  # eat the 'fn' token

        if self.__eat_token().type != TokenType.Lparen:
            raise Exception(f"Expected '(' got '{self.__cur_token().value}' at [ln: {self.__cur_token().ln}]")

        params = self.__parse_args()

        if self.__eat_token().type != TokenType.LBrace:
            raise Exception("Expected '{' got " + f"'{self.__cur_token().value}' as function declarations cannot as expressions and return no value")

        body = []
        while self.__cur_token().type != TokenType.RBrace:
            body.append(self.__parse_stmt())

        if self.__eat_token().type != TokenType.RBrace:
            raise SyntaxError(
                "Expected '}' got " + f"'{self.__cur_token().value}' instead"
            )

        return asts.FunctionExpr("FunctionExpr", params, body)

    def __parse_assignment_expr(self) -> asts.Expr:
        lhs = self.__parse_array_expr()

        if (
            self.__cur_token().type == TokenType.Assign
            or self.__cur_token().value in ("+=", "-=", "/=", "*=", "%=")
            or self.__cur_token().type is TokenType.PostFix
        ):
            if self.__cur_token().type == TokenType.BinOp:
                return self.__parse_shorthand_binexpr(lhs)
            elif self.__cur_token().type == TokenType.PostFix:
                return self.__parse_postfix_expr(lhs)

            self.__eat_token()  # eat '=' token

            rhs = self.__parse_expr()

            return asts.AssignmentExpr("AssignmentExpr", lhs, rhs)  # type: ignore

        return lhs

    def __parse_postfix_expr(self, left) -> asts.AssignmentExpr:
        if self.__cur_token().value == "++":
            self.__eat_token()
            result = asts.AssignmentExpr(
                "AssignmentExpr",
                left,
                asts.BinaryExpr(
                    "BinExpr",
                    self.__parse_primary(left.symbol),
                    Token(TokenType.BinOp, "+", self.__cur_token().ln),
                    asts.NumericLiteral("NumericLiteral", 1.0),
                ),
            )
        else:
            self.__eat_token()
            result = asts.AssignmentExpr(
                "AssignmentExpr",
                left,
                asts.BinaryExpr(
                    "BinExpr",
                    self.__parse_primary(left.symbol.symbol),
                    Token(TokenType.BinOp, "-", self.__cur_token().ln),
                    asts.NumericLiteral("NumericLiteral", 1.0),
                ),
            )

        return result

    def __parse_shorthand_binexpr(self, left) -> asts.AssignmentExpr:
        if self.__cur_token().value == "+=":
            self.__eat_token()

            result = asts.AssignmentExpr(
                "AssignmentExpr",
                left,
                asts.BinaryExpr(
                    "BinExpr",
                    self.__parse_primary(left.symbol.symbol),
                    Token(TokenType.BinOp, "+", self.__cur_token().ln),
                    self.__parse_expr(),
                ),
            )
        elif self.__cur_token().value == "-=":
            self.__eat_token()

            result = asts.AssignmentExpr(
                "AssignmentExpr",
                left,
                asts.BinaryExpr(
                    "BinExpr",
                    self.__parse_primary(left.symbol.symbol),
                    Token(TokenType.BinOp, "-", self.__cur_token().ln),
                    self.__parse_expr(),
                ),
            )
        elif self.__cur_token().value == "/=":
            self.__eat_token()

            result = asts.AssignmentExpr(
                "AssignmentExpr",
                left.symbol,
                asts.BinaryExpr(
                    "BinExpr",
                    self.__parse_primary(left.symbol.symbol),
                    Token(TokenType.BinOp, "/", self.__cur_token().ln),
                    self.__parse_expr(),
                ),
            )
        elif self.__cur_token().value == "*=":
            self.__eat_token()

            result = asts.AssignmentExpr(
                "AssignmentExpr",
                left.symbol,
                asts.BinaryExpr(
                    "BinExpr",
                    self.__parse_primary(left),
                    Token(TokenType.BinOp, "*", self.__cur_token().ln),
                    self.__parse_expr(),
                ),
            )
        else:
            self.__eat_token()

            result = asts.AssignmentExpr(
                "AssignmentExpr",
                left.symbol,
                asts.BinaryExpr(
                    "BinExpr",
                    self.__parse_primary(left),
                    Token(TokenType.BinOp, "%", self.__cur_token().ln),
                    self.__parse_expr(),
                ),
            )

        return result

    def __parse_array_expr(self) -> asts.Expr:
        if self.__cur_token().type != TokenType.Lbrack:
            return self.__parse_object_expr()

        self.__eat_token()  # eat '[' token
        properties = [self.__parse_expr()]

        while (
            self.__cur_token().type == TokenType.Comma
            and self.__cur_token().type != TokenType.Rbrack
        ):
            self.__eat_token()  # eat the ',' token
            properties.append(self.__parse_expr())

        if self.__cur_token().type != TokenType.Rbrack:
            raise SyntaxError(
                f"Unexpected token recieved, expected ']' got {self.__cur_token().value} at {self.__cur_token().ln}"
            )

        self.__eat_token()
        array = asts.ArrayLiteral("ArrayLiteral", properties)

        return array

    def __parse_object_expr(self) -> asts.Expr:
        if self.__cur_token().type != TokenType.LBrace:
            return self.__parse_or_expr()  # type: ignore

        properties: List[asts.Property] = []

        while self.__not_eof() and self.__cur_token().type != TokenType.RBrace:
            self.__eat_token()

            key = self.__eat_token()

            if key.type != TokenType.Ident:
                raise TypeError(
                    f"key of maps can only be an identifier not '{self.__cur_token().type}'"
                )

            # Allow shorthand object expressions { key } {key, }

            if self.__cur_token().type == TokenType.Comma:
                self.__eat_token()  # consume the ',' token

                properties.append(asts.Property("Property", key, None))
                continue
            elif self.__cur_token().type == TokenType.RBrace:
                properties.append(asts.Property("Property", key, None))
                continue

            if self.__eat_token().type != TokenType.Colon:
                raise SyntaxError(
                    f"Expected ':' got '{self.__cur_token().value}' intead at [ln: {self.__cur_token().ln}]"
                )

            value = self.__parse_expr()

            properties.append(asts.Property("Property", key, value))  # type: ignore

            if (
                self.__cur_token().type != TokenType.RBrace
                and self.__cur_token().type != TokenType.Comma
            ):
                raise SyntaxError(
                    "Expected ',' or '}' got"
                    + f"'{self.__cur_token().value}' at [ln: {self.__cur_token().ln}]"
                )

        if self.__eat_token().type != TokenType.RBrace:
            raise SyntaxError(
                "Expected '}' got"
                + f"'{self.__cur_token().value}' at [ln: {self.__cur_token().ln}]"
            )

        return asts.MapLiteral("MapLiteral", properties)

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
                self.__parse_member_expr(),
            )

        return self.__parse_member_expr()

    def __parse_member_expr(self) -> asts.Expr:
        obj = self.__parse_call_expr()

        while (
            self.__cur_token().type == TokenType.Dot
            or self.__cur_token().type == TokenType.Lbrack
        ):
            operator = self.__eat_token()

            property: Optional[asts.Expr]
            computed: bool

            if operator.type == TokenType.Dot:
                computed = False
                property = self.__parse_call_expr()
            else:
                computed = True
                property = self.__parse_expr()

                if self.__eat_token().type != TokenType.Rbrack:
                    raise SyntaxError(
                        f"Unclosed '[' literal goten at [ln: {self.__cur_token().ln}]"
                    )

            obj = asts.MemberExpr("MemberExpr", obj, property, computed)  # type: ignore

        return obj  # type: ignore

    def __parse_call_expr(self) -> asts.Expr:
        caller = self.__parse_primary(self.__eat_token())
        args = None

        while self.__cur_token().type == TokenType.Lparen:
            self.__eat_token()
            args = self.__parse_args()

            caller = asts.CallExpr("CallExpr", caller, args)

        return caller

    def __parse_args(self) -> List[asts.Expr]:
        args = (
            [self.__parse_expr()] if self.__cur_token().type != TokenType.Rparen else []
        )

        while (
            self.__cur_token().type == TokenType.Comma
            and self.__cur_token().type != TokenType.Rparen
        ):
            self.__eat_token()
            args.append(self.__parse_expr())

        if self.__cur_token().type != TokenType.Rparen:
            raise SyntaxError(
                f"Syntax Error expected ')', got '{self.__cur_token().value}' during function call instead at [ln: {self.__cur_token().ln}]"
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
