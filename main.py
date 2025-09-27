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

parsed_lines = [parser.parse_line(line) for line in cleaned_lines]
output = parser.output(parsed_lines)

print(f"{output:b}")

with open(sys.argv[2], "wb") as f:
    f.write(output.to_bytes(length=output.bit_length(), byteorder="big"))
