from typing import List

from .tokens import Token, TokenType, keywords


class Lexer:
    def __init__(self, input: str) -> None:
        self.input = input
        self.pos = 0
        self.line = 1
        self.char = self.input[self.pos]

    def __advance(self):
        self.pos += 1

        if self.char == "\n":
            self.line += 1

        if self.pos >= len(self.input):
            self.char = "\0"
        else:
            self.char = self.input[self.pos]

    def __skip_whitespace(self):
        while (
            self.char == " "
            or self.char == "\t"
            or self.char == "\r"
            or self.char == "\n"
        ):
            self.__advance()

    def tokenize(self) -> Token:
        self.__skip_whitespace()

        match self.char:
            case "\0":
                token = Token(TokenType.Eof, self.char, self.line)
            case "-":
                if self.pos < len(self.input) - 1 and self.input[self.pos + 1] == "=":
                    self.__advance()  # "moves to the second equals"
                    token = Token(TokenType.BinOp, "-=", self.line)

                    self.__advance()  # leaves the second '='
                    return token
                elif self.pos < len(self.input) - 1 and self.input[self.pos + 1] == "-":
                    self.__advance()  # "moves to the second equals"
                    token = Token(TokenType.PostFix, "--", self.line)

                    self.__advance()  # leaves the second '='
                    return token
                
                token = Token(TokenType.BinOp, self.char, self.line)
            case "*":
                if self.pos < len(self.input) - 1 and self.input[self.pos + 1] == "=":
                    self.__advance()  # "moves to the second equals"
                    token = Token(TokenType.BinOp, "*+=", self.line)

                    self.__advance()  # leaves the second '='
                    return token
                token = Token(TokenType.BinOp, self.char, self.line)
            case "/":
                if self.pos < len(self.input) - 1 and self.input[self.pos + 1] == "/":
                    while self.char != "\n" and self.char != "\0":
                        self.__advance()

                    return self.tokenize()
                
                if self.pos < len(self.input) - 1 and self.input[self.pos + 1] == "=":
                    self.__advance()  # "moves to the second equals"
                    token = Token(TokenType.BinOp, "/=", self.line)

                    self.__advance()  # leaves the second '='
                    return token

                token = Token(TokenType.BinOp, self.char, self.line)
            case "+":
                if self.pos < len(self.input) - 1 and self.input[self.pos + 1] == "=":
                    self.__advance()  # "moves to the second equals"
                    token = Token(TokenType.BinOp, "+=", self.line)

                    self.__advance()  # leaves the second '='
                    return token
                
                elif self.pos < len(self.input) - 1 and self.input[self.pos + 1] == "+":
                    self.__advance()  # "moves to the second equals"
                    token = Token(TokenType.PostFix, "++", self.line)

                    self.__advance()  # leaves the second '='
                    return token
                
                token = Token(TokenType.BinOp, self.char, self.line)
            case "%":
                if self.pos < len(self.input) - 1 and self.input[self.pos + 1] == "=":
                    self.__advance()  # "moves to the second equals"
                    token = Token(TokenType.BinOp, "%=", self.line)

                    self.__advance()  # leaves the second '='
                    return token
                token = Token(TokenType.BinOp, self.char, self.line)
            case ",":
                if self.pos < len(self.input) - 1 and self.input[self.pos + 1] == "=":
                    self.__advance()  # "moves to the second equals"
                    token = Token(TokenType.Equals, "=", self.line)

                    self.__advance()  # leaves the second '='
                    return token
                token = Token(TokenType.Comma, self.char, self.line)
            case ">":
                if self.pos < len(self.input) - 1 and self.input[self.pos + 1] == "=":
                    self.__advance()  # "moves to the second equals"
                    token = Token(TokenType.BinOp, ">=", self.line)

                    self.__advance()  # leaves the '='
                    return token

                token = Token(TokenType.BinOp, self.char, self.line)
            case "<":
                if self.pos < len(self.input) - 1 and self.input[self.pos + 1] == "=":
                    self.__advance()  # "moves to the second equals"
                    token = Token(TokenType.BinOp, "<=", self.line)

                    self.__advance()  # leaves the second '='
                    return token

                token = Token(TokenType.BinOp, self.char, self.line)
            case "!":
                if self.pos < len(self.input) - 1 and self.input[self.pos + 1] == "=":
                    self.__advance()  # moves to the 'equals

                    token = Token(TokenType.NotEq, "!=", self.line)
                    self.__advance()

                    return token
                token = Token(TokenType.Bang, self.char, self.line)

            case "(":
                token = Token(TokenType.Lparen, self.char, self.line)
            case ")":
                token = Token(TokenType.Rparen, self.char, self.line)
            case "{":
                token = Token(TokenType.LBrace, self.char, self.line)
            case "}":
                token = Token(TokenType.RBrace, self.char, self.line)
            case "[":
                token = Token(TokenType.Lbrack, self.char, self.line)
            case "]":
                token = Token(TokenType.Rbrack, self.char, self.line)
            case ".":
                token = Token(TokenType.Dot, self.char, self.line)
            case '"' | "'":
                literal = self.__make_string(
                    self.char,
                )
                token = Token(TokenType.String, literal, self.line)
            case "`":
                token = Token(
                    TokenType.String, self.__make_multiline_string(self.char), self.line
                )
            case "=":
                if self.pos < len(self.input) - 1 and self.input[self.pos + 1] == "=":
                    self.__advance()  # "moves to the second equals"
                    token = Token(TokenType.Equals, "==", self.line)

                    self.__advance()  # leaves the second '='
                    return token

                token = Token(TokenType.Assign, self.char, self.line)
            case _:
                if is_letter(self.char):
                    literal = self.__make_ident()

                    if literal in keywords:
                        return Token(keywords[literal], literal, self.line)

                    return Token(TokenType.Ident, literal, self.line)
                elif is_number(self.char):
                    return Token(TokenType.Number, self.__make_number(), self.line)

                raise SyntaxError(
                    f"got '{self.char}' at [ln: {self.line}, col: {self.pos}]"
                )

        self.__advance()
        return token

    def __make_ident(self) -> str:
        pos = self.pos

        while is_letter(self.char) or is_number(self.char) or self.char == "_":
            self.__advance()

        return self.input[pos : self.pos]

    def __make_number(self) -> str:
        pos = self.pos
        dot_count = 0

        while is_number(self.char) and dot_count < 2 or self.char == ".":
            if self.char == ".":
                dot_count += 1

            self.__advance()

        if dot_count > 1:
            raise SyntaxError(f"got '.' at [ln: {self.line}, col: {self.pos - 1}]")

        return self.input[pos : self.pos]

    def __make_string(self, quote: str) -> str:
        self.__advance()  # advance past the starting quote
        pos = self.pos

        while self.char != quote and self.char != "\n":
            self.__advance()

        if self.char != quote:
            raise SyntaxError(
                f"Unterminated string literal gotten at [ln: {self.line}, col: {self.pos}]"
            )

        return self.input[pos : self.pos]

    def __make_multiline_string(self, quote: str) -> str:
        self.__advance()  # advance past the starting quote
        pos = self.pos

        while self.char != quote:
            self.__advance()

        return self.input[pos : self.pos]


def is_letter(char: str) -> bool:
    if char == "\0":
        return False

    return char >= "a" and char <= "z" or char >= "A" and char <= "Z"


def is_number(char: str) -> bool:
    if char == "\0":
        return False

    return char >= "0" and char <= "9"


def tokenize(input: str) -> List[Token]:
    lexer = Lexer(input)
    tokens = [lexer.tokenize()]

    while tokens[-1].type != TokenType.Eof:
        tokens.append(lexer.tokenize())

    return tokens
