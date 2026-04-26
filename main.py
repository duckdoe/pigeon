import sys

from frontend.lexer import tokenize
from frontend.parser import Parser
from runtime.interpreter import Intpereter


def eval(input: str):
    tokens = tokenize(input)
    tree = Parser(tokens).generate_ast()

    print(Intpereter(tree).eval())


def run_program():
    try:
        _, file = sys.argv

        with open(file) as f:
            content = f.read()

        eval(content)
    except ValueError:
        print("Welcome pigeon v0.0.1, start typing have fun \\(^-^)/")

        while True:
            code = input("> ").strip()
            if code == "exit":
                break

            eval(code)


run_program()
