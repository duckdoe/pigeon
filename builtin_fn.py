from typing import List
from runtime.values import RuntimeValue, String, Number, Null

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


def lenfn(args: List[RuntimeValue]) -> Number:
    if len(args) > 1:
        raise TypeError(f"Expected 1 argument got {len(args)}")

    arg = args[0]

    if arg.type == "string" or arg.type == "array":
        return Number("number", float(len(arg.value)))  # type: ignore

    raise TypeError(f"Value of type '{arg.type}' has no len()")


def formatfn(args: List[RuntimeValue]) -> String:
    if len(args) < 1:
        raise TypeError(f"Expected 1 argument got {len(args)}")

    if args[0].type != "string":
        raise TypeError(
            f"The first argument must be of type 'string' instead got {args[0].type}"
        )

    string = args.pop(0).value  # type: ignore

    while args:
        fstring = string.count("{}")

        if len(args) < fstring:
            raise TypeError(
                "Mismatched amout of arguments gotten, have %s '{}' but got %d values",
                len(args),
                fstring,
            )
        string = string.replace("{}", args.pop(0).value)  # type: ignore

    return String("string", string)


def typefn(args: List[RuntimeValue]):
    if len(args) > 1:
        raise TypeError(f"Expected 1 argument got {len(args)}")

    arg = args[0]
    return String("string", arg.type)