import sys
from typing import List

from frontend.lexer import tokenize
from frontend.parser import Parser
from runtime.environment import Environment
from runtime.interpreter import Intpereter
from runtime.values import NativeFn, Null, RuntimeValue


def eval(input: str, env):
    tokens = tokenize(input)
    tree = Parser(tokens).generate_ast()

    Intpereter(tree).eval(env)


def printlnfn(args: List[RuntimeValue]) -> Null:
    result = ""

    for arg in args:
        if arg.type == "nativefn":
            result += "[NativeFn]"
        result += str(arg.value) + " "  # type: ignore

    print(result)
    return Null("null")


def run_program():
    env = Environment()
    env.declare_var("println", NativeFn("nativefn", printlnfn), True)
    try:
        _, file = sys.argv

        with open(file) as f:
            content = f.read()

        eval(content, env)
    except ValueError:
        print("Welcome pigeon v0.0.1, start typing have fun \\(^-^)/")

        while True:
            code = input("> ").strip()
            if code == "exit":
                break

            eval(code, env)


run_program()
