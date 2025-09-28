import sys

import parser

if len(sys.argv) < 3:
    print("Usage: python main.py <input> <output>")
    exit(0)

assert len(sys.argv) > 2

lines = None
with open(sys.argv[1], "r") as f:
    lines = f.readlines()

assert lines is not None

cleaned_lines = parser.clean_lines(lines)

sections = parser.parse_sections(cleaned_lines)

start_section = next(
    (s for s in sections if s.name == "start" or s.name == "_start"), None
)

assert start_section is not None

if start_section.name.startswith("_"):
    raise Exception(f"Start section must be inline @ {start_section.offset}")

inline_sections = parser.compile_inline(sections)

output = parser.output(inline_sections["start"])

print(f"{output:b}")

with open(sys.argv[2], "wb") as f:
    f.write(output.to_bytes(length=output.bit_length(), byteorder="big"))
