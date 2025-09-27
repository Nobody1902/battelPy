import itertools
import defs


def _collapse_spaces(s: str) -> str:
    parts = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] in (" ", "\t"):
            parts.append(" ")
            i += 1
            while i < n and s[i] in (" ", "\t"):
                i += 1
        else:
            parts.append(s[i])
            i += 1
    return "".join(parts)


def clean_lines(text: list[str]) -> list[str]:
    return [
        collapsed.replace(", ", ",")  # For easier parsing
        for collapsed in (
            _collapse_spaces(line.split(";", 1)[0].strip(" \t\n")) for line in text
        )
        if collapsed != ""
    ]


def _parse_register(arg):
    if arg.upper() in defs.REGISTERS.__members__:
        return defs.REGISTERS[arg.upper()].value

    raise Exception(f"Unknown register: {arg}")


def _parse_value(arg, max_size=5):
    if arg.startswith("-"):
        raise Exception("Value cannot be negative")

    if arg.isdigit():
        value = int(arg)
    elif arg.startswith("0b"):
        value = int(arg, 2)
    elif arg.startswith("0x"):
        value = int(arg, 16)
    elif arg.startswith("0o"):
        value = int(arg, 8)
    else:
        raise ValueError(f"Unknown value: {arg}")

    if value.bit_length() > max_size:
        raise ValueError(f"Value {value} exceeds maximum size of {max_size}b")

    return value


def _parse_arguments(args: list[str], op_signiture) -> list:
    arguments = []

    if len(op_signiture["args"]) == 0:
        return arguments

    args = args[0].split(",")

    arg_sizes = op_signiture.get("arg_sizes", [5] * len(args))

    for i, arg in enumerate(args):
        arg_type = op_signiture["args"][i]

        if arg_type == defs.ArgumentType.REGISTER:
            arguments.append(_parse_register(arg))
        elif arg_type == defs.ArgumentType.VALUE:
            arguments.append(_parse_value(arg, arg_sizes[i]))
        elif arg_type == defs.ArgumentType.VALUE_OR_REGISTER:
            if arg.upper() in defs.REGISTERS.__members__:
                arguments.append(_parse_register(arg))
            else:
                arguments.append(_parse_value(arg, arg_sizes[i]))

    return arguments


def parse_line(line: str):
    operation, *args = line.split(" ")

    if operation.upper() not in defs.OPERATIONS:
        raise Exception(f"Unknown operation: {operation}")

    op_signiture = defs.OPERATIONS[operation.upper()]

    arguments = _parse_arguments(args, op_signiture)

    return (op_signiture["code"], arguments)


def output(parsed_lines: list[tuple[int, list[int]]]) -> int:
    output = ""

    for line in parsed_lines:
        line_output = f"{line[0]:b}"

        arguments = line[1]
        op_signiture = [v for v in defs.OPERATIONS.values() if v["code"] == line[0]][0]

        # Default to 5 bits
        arg_sizes = list(itertools.repeat(5, len(op_signiture["args"])))
        if "arg_sizes" in op_signiture:
            arg_sizes = op_signiture["arg_sizes"]

        for i, arg in enumerate(arguments):
            size = arg_sizes[i]
            line_output += f"{arg:0{size}b}"

        output += f"{line_output:0<16}"

    return int(output, 2)
