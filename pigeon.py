import sys

from builtin_fn import formatfn, lenfn, printlnfn, typefn, timefn
from frontend.lexer import tokenize
from frontend.parser import Parser
from runtime.environment import Environment
from runtime.interpreter import Intpereter
from runtime.values import NativeFn


def eval(input: str, env):
    tokens = tokenize(input)
    tree = Parser(tokens).generate_ast()

    Intpereter(tree).eval(env)



def run_program():
    env = Environment()
    env.declare_var("println", NativeFn("nativefn", printlnfn), True)
    env.declare_var("len", NativeFn("nativefn", lenfn), True)
    env.declare_var("format", NativeFn("nativefn", formatfn), True)
    env.declare_var("type", NativeFn("nativefn", typefn), True)
    env.declare_var("time", NativeFn("nativefn", timefn), True)
    try:
        _, file = sys.argv

        with open(file) as f:
            content = f.read()

        eval(content, env)
    except TypeError as e:
        msg = e.args[0]
        print(f"TypeError: {msg}")
    except SyntaxError as e:
        msg = e.args[0]
        print(f"SyntaxError: {msg}")
    except ValueError:
        print("Welcome pigeon v0.0.1, start typing have fun \\(^-^)/")

        while True:
            code = input("> ").strip()
            if code == "exit":
                break

            eval(code, env)
    except Exception as e:
        msg = e.args[0]
        print(f"UncaughtError: {msg}")


run_program()
