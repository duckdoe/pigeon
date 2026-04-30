from typing import List

from runtime.values import Null, Number, RuntimeValue, String, Array, Boolean


def timefn(args: List[RuntimeValue]) -> Number:
    if args:
        raise TypeError(f"Expected 0 arguments got {len(args)}")

    from time import time

    current_time = time()
    return Number("number", current_time)


def inputfn(args: List[RuntimeValue]) -> String:
    if len(args) != 1:
        raise TypeError(f"Expected only one argument got {len(args)}")

    value = input(args[0].value)  # type: ignore

    return String("string", value)


def to_numberfn(args: List[RuntimeValue]) -> Number:
    if len(args) != 1:
        raise TypeError(f"Expected only one argument got {len(args)}")

    if args[0].type != "string":
        raise TypeError(f"Cannot convert type '{args[0].type}' to a number")

    value = args[0].value  # type: ignore

    try:
        value = float(value)
        return Number("number", value)
    except Exception:
        error = f"Cannot convert '{value}' to number"

    raise TypeError(error)


def to_stringfn(args: List[RuntimeValue]) -> String:
    if len(args) != 1:
        raise TypeError(f"Expected only one argument got {len(args)}")

    return String("string", str(args[0].value))  # type: ignore


def to_booleanfn(args: List[RuntimeValue]) -> Boolean:
    if len(args) != 1:
        raise TypeError(f"Expected only one argument got {len(args)}")

    arg = args[0]
    if arg.type != "string" and arg.value not in ("true", "false"):  # type: ignore
        raise TypeError(
            f"Cannot convert type '{arg.type}' of value '{arg.value}' to a boolean datatype"
        )  # type: ignore

    return Boolean("boolean", arg.value)  # type: ignore


def appendfn(args: List[RuntimeValue]) -> Array:
    if len(args) < 2:
        raise TypeError(f"Expected atleast 2 arguments got {len(args)}")

    arr = args.pop(0)

    arr = Array("array", arr.value)  # type: ignore

    if arr.type != "array":
        raise TypeError(f"Cannot append to {arr.type}")

    while args:
        arr.value.append(args.pop(0))

    return arr


def return_string(arg: RuntimeValue):
    if arg.type == "nativefn":
        return "[NativeFn]"
    elif arg.type == "array":
        result = "["

        for i in range(len(arg.value) - 1):  # type: ignore
            result += return_string(arg.value[i]) + ", "  # type: ignore

        result += return_string(arg.value[-1]) + "]"  # type: ignore

        return result
    elif arg.type == "string":
        result = '"'
        result += arg.value  # type: ignore
        result += '"'
        return result
    elif arg.type == "map":
        result = "{"

        for key, value in arg.properties.items():  # type: ignore
            result += key + ": " + return_string(value) + ", "

        result = result[0:-2]
        result += "}"
        print(result)
        return result
    elif arg.type == "number":
        number = arg.value  # type: ignore

        if number % 1 == 0:
            return str(int(number))

        return str(number)
    else:
        return str(arg.value)  # type: ignore


def printlnfn(args: List[RuntimeValue]) -> Null:
    result = ""

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

        string = string.replace("{}", str(args.pop(0).value), 1)  # type: ignore

    return String("string", string)


def typefn(args: List[RuntimeValue]):
    if len(args) > 1:
        raise TypeError(f"Expected 1 argument got {len(args)}")

    arg = args[0]
    return String("string", arg.type)
