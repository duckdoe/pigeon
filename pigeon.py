import sys

from frontend.lexer import tokenize
from frontend.parser import Parser
from runtime.environment import Environment
from runtime.interpreter import Intpereter
from runtime.values import Number


def eval(input: str, env):
    tokens = tokenize(input)
    tree = Parser(tokens).generate_ast()

    print(Intpereter(tree).eval(env))


def run_program():
    try:
        _, file = sys.argv
        env = Environment()

        with open(file) as f:
            content = f.read()

        eval(content, env)
    except ValueError:
        print("Welcome pigeon v0.0.1, start typing have fun \\(^-^)/")
        env = Environment()
        env.declare_var("x", Number("number", 12))

        while True:
            code = input("> ").strip()
            if code == "exit":
                break

            eval(code, env)


run_program()
