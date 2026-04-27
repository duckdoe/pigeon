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

    def return_string(arg: RuntimeValue):
        if arg.type == "nativefn":
            return "[NativeFn]"
        elif arg.type == "array":
            result = "["

            for i in range(len(arg.value) - 1):  # type: ignore
                result += return_string(arg.value[i]) + ", "  # type: ignore

            result += return_string(arg.value[-1]) + "]"  # type: ignore

            return result

        else:
            return str(arg.value)  # type: ignore

    for arg in args:
        result = return_string(arg) + " "

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
