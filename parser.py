import itertools
import defs
import sys


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


def _parse_register(arg: str, i: int):
    if arg.upper() in defs.REGISTERS.__members__:
        return defs.REGISTERS[arg.upper()].value

    raise Exception(f'Unknown register: "{arg}" @ {i + 1}')


def _parse_value(arg: str, i: int, max_size=5):
    if arg.startswith("-"):
        raise Exception(f'Value cannot be negative: "{arg}" @ {i + 1}')

    if arg.isdigit():
        value = int(arg)
    elif arg.startswith("0b"):
        value = int(arg, 2)
    elif arg.startswith("0x"):
        value = int(arg, 16)
    elif arg.startswith("0o"):
        value = int(arg, 8)
    else:
        raise ValueError(f'Unknown value: "{arg}" @ {i + 1}')

    if value.bit_length() > max_size:
        raise ValueError(f"Value {value} exceeds maximum size of {max_size}b @ {i + 1}")

    return value


def _parse_arguments(args: list[str], op_signiture, line_idx: int) -> list:
    arguments = []

    if len(op_signiture["args"]) == 0:
        return arguments

    args = args[0].split(",")

    arg_sizes = op_signiture.get("arg_sizes", [5] * len(args))

    for i, arg in enumerate(args):
        arg_type = op_signiture["args"][i]

        if arg_type == defs.ArgumentType.REGISTER:
            arguments.append(_parse_register(arg, line_idx))
        elif arg_type == defs.ArgumentType.VALUE:
            arguments.append(_parse_value(arg, arg_sizes[i]))
        elif arg_type == defs.ArgumentType.VALUE_OR_REGISTER:
            if arg.upper() in defs.REGISTERS.__members__:
                arguments.append(_parse_register(arg, line_idx))
            else:
                arguments.append(_parse_value(arg, arg_sizes[i]))

    return arguments


def parse_line(line: str, i: int) -> tuple[int, list[int]]:
    operation, *args = line.split(" ")

    if operation.upper() not in defs.OPERATIONS:
        raise Exception(f'Unknown operation: "{operation}" @ {i + 1}')

    op_signiture = defs.OPERATIONS[operation.upper()]

    arguments = _parse_arguments(args, op_signiture, i)

    return (op_signiture["code"], arguments)


def parse_lines(
    lines: list[str],
    offset: int,
) -> list[tuple[int, list[int]]]:
    result = []
    for i, line in enumerate(lines):
        if line.startswith("@"):
            result.append(line.removeprefix("@"))
            continue

        result.append(parse_line(line, i + offset))

    return result


def parse_sections(lines: list[str]) -> list[defs.Section]:
    sections = {}
    for i, line in enumerate(lines):
        if not line.endswith(":"):
            continue

        if " " in line:
            raise Exception(f'Section declaration contains space: "{line}" @ {i + 1}')

        sections[i] = line.removesuffix(":")

    result = []

    sorted_keys = sorted(sections.keys())

    for i, start in enumerate(sorted_keys):
        end = sorted_keys[i + 1] if i + 1 < len(sorted_keys) else len(lines)
        section_name = sections[start]
        inline = not section_name.startswith("_")
        result.append(
            defs.Section(section_name, lines[start + 1 : end], inline, start + 1)
        )

    return result


def resolve_inline_sections(
    sections, max_allowed_depth=None
) -> dict[str, list[tuple[int, list[int]]]]:
    max_allowed_depth = (
        sys.getrecursionlimit() - 100 if not max_allowed_depth else max_allowed_depth
    )
    resolved = {}
    visited = set()
    depth_map = {}

    def resolve_section(name, depth=0):
        if depth > max_allowed_depth:
            raise RecursionError(
                f'Maximum recursion depth of {max_allowed_depth} exceeded at section "{name}"'
            )

        if name in resolved:
            return resolved[name]

        if name not in sections:
            raise Exception(f'Section "{name}" is undefined')

        visited.add(name)
        raw_items = sections[name]
        result = []
        max_depth = depth

        for item in raw_items:
            if isinstance(item, str):
                sub_result, sub_depth = resolve_section(item, depth + 1)
                result.extend(sub_result)
                max_depth = max(max_depth, sub_depth)
            elif isinstance(item, tuple):
                result.append(item)
            else:
                raise TypeError(f"Unexpected item type in section '{name}': {item}")

        resolved[name] = result
        depth_map[name] = max_depth
        return result, max_depth

    for section in sections:
        if section not in resolved:
            resolve_section(section)

    sorted_keys = sorted(sections.keys(), key=lambda k: depth_map[k], reverse=True)

    output = {key: resolved[key] for key in sorted_keys}
    # max_depth_overall = max(depth_map.values(), default=0)

    return output


def compile_inline(
    sections: list[defs.Section],
) -> dict[str, list[tuple[int, list[int]]]]:
    result = {}
    for section in sections:
        if not section.inline:
            continue

        result[section.name] = parse_lines(section.lines, section.offset)

    return resolve_inline_sections(result)


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
