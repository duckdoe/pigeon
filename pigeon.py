import sys
from os import path

from builtin_fn import (
    formatfn,
    lenfn,
    printlnfn,
    typefn,
    timefn,
    appendfn,
    inputfn,
    to_numberfn,
    to_booleanfn,
)
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
    env.declare_var("append", NativeFn("nativefn", appendfn), True)
    env.declare_var("input", NativeFn("nativefn", inputfn), True)
    env.declare_var("to_number", NativeFn("nativefn", to_numberfn), True)
    env.declare_var("to_boolean", NativeFn("nativefn", to_booleanfn), True)
    try:
        _, file = sys.argv
        
        ext = file.split('.')
        if ext[-1] != 'pg':
            print("Usage python pigeon.py [script].pg")
            return
        
        if not path.exists(file):
            print(f"Cannot open '{file}' as it does not exist")

        with open(file) as f:
            content = f.read()

        if content.strip() == '':
            return

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
