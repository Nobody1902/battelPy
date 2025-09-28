from enum import Enum
from dataclasses import dataclass


class ArgumentType(Enum):
    VALUE = 0b00
    REGISTER = 0b10
    VALUE_OR_REGISTER = 0b11


OPERATIONS = {
    # arg_sizes: default is 5
    "LDI": {"args": [ArgumentType.VALUE], "code": 0b0, "arg_sizes": [15]},
    "FLAG": {"args": [], "code": 0b111111},
    # Register + register or value
    "MV": {
        "args": [ArgumentType.REGISTER, ArgumentType.VALUE_OR_REGISTER],
        "code": 0b100000,
    },
    "ADD": {
        "args": [ArgumentType.REGISTER, ArgumentType.VALUE_OR_REGISTER],
        "code": 0b100001,
    },
    "SUB": {
        "args": [ArgumentType.REGISTER, ArgumentType.VALUE_OR_REGISTER],
        "code": 0b100010,
    },
    "NOT": {"args": [ArgumentType.REGISTER], "code": 0b100011},
    "AND": {
        "args": [ArgumentType.REGISTER, ArgumentType.VALUE_OR_REGISTER],
        "code": 0b100100,
    },
    "OR": {
        "args": [ArgumentType.REGISTER, ArgumentType.VALUE_OR_REGISTER],
        "code": 0b100101,
    },
    "XOR": {
        "args": [ArgumentType.REGISTER, ArgumentType.VALUE_OR_REGISTER],
        "code": 0b100110,
    },
    "SHL": {
        "args": [ArgumentType.REGISTER, ArgumentType.VALUE_OR_REGISTER],
        "code": 0b100111,
    },
    "SHR": {
        "args": [ArgumentType.REGISTER, ArgumentType.VALUE_OR_REGISTER],
        "code": 0b101000,
    },
    # Control flow
    "JMP": {"args": [ArgumentType.REGISTER], "code": 0b101001},
    "JZ": {
        "args": [ArgumentType.REGISTER, ArgumentType.VALUE_OR_REGISTER],
        "code": 0b101010,
    },
    "JNZ": {
        "args": [ArgumentType.REGISTER, ArgumentType.VALUE_OR_REGISTER],
        "code": 0b101011,
    },
    "JN": {
        "args": [ArgumentType.REGISTER, ArgumentType.VALUE_OR_REGISTER],
        "code": 0b101100,
    },
    "JP": {
        "args": [ArgumentType.REGISTER, ArgumentType.VALUE_OR_REGISTER],
        "code": 0b101101,
    },
    # Memory
    "LD": {"args": [ArgumentType.REGISTER, ArgumentType.REGISTER], "code": 0b101110},
    "ST": {"args": [ArgumentType.REGISTER, ArgumentType.REGISTER], "code": 0b101111},
    # Stack
    "PUSH": {"args": [ArgumentType.REGISTER], "code": 0b110000},
    "POP": {"args": [ArgumentType.REGISTER], "code": 0b110001},
    # Register + immediate
    "ADDI": {"args": [ArgumentType.REGISTER, ArgumentType.VALUE], "code": 0b110010},
    "SUBI": {"args": [ArgumentType.REGISTER, ArgumentType.VALUE], "code": 0b110011},
    "SHLI": {"args": [ArgumentType.REGISTER, ArgumentType.VALUE], "code": 0b110100},
    "SHRI": {"args": [ArgumentType.REGISTER, ArgumentType.VALUE], "code": 0b110101},
}


class REGISTERS(Enum):
    R0 = 0x0
    R1 = 0x1
    R2 = 0x2
    R3 = 0x3
    R4 = 0x4
    R5 = 0x5
    R6 = 0x6
    R7 = 0x7
    R8 = 0x8
    R9 = 0x9
    R10 = 0xA
    R11 = 0xB
    R12 = 0xC
    R13 = 0xD
    R14 = 0xE
    R15 = 0xF
    R16 = 0x10
    R17 = 0x11
    R18 = 0x12
    R19 = 0x13
    R20 = 0x14
    R21 = 0x15
    R22 = 0x16
    R23 = 0x17
    R24 = 0x18
    R25 = 0x19
    # Reserved
    R26 = 0x1A
    R27 = 0x1B
    R28 = 0x1C
    R29 = 0x1D
    SP = 0x1E
    PC = 0x1F


@dataclass
class Section:
    name: str
    lines: list[str]
    inline: bool
    relative_offset: int
    offset: int
