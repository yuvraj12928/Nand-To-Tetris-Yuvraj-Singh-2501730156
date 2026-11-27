#!/usr/bin/env python3
"""
Hack assembler for the Nand2Tetris capstone.
K = 46 -> extra feature: invalid instructions produce a line-numbered error.
Usage: python assembler.py Box.asm [output.hack]
"""
import sys
from pathlib import Path

PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576,
}
for i in range(16):
    PREDEFINED[f"R{i}"] = i

DEST = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111",
}
JUMP = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}
COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "M": "1110000",
    "!D": "0001101", "!A": "0110001", "!M": "1110001",
    "-D": "0001111", "-A": "0110011", "-M": "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
    "D+A": "0000010", "D+M": "1000010",
    "D-A": "0010011", "D-M": "1010011",
    "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "D&M": "1000000",
    "D|A": "0010101", "D|M": "1010101",
}

def clean_lines(path):
    result = []
    for number, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("//", 1)[0].strip()
        if line:
            result.append((number, line))
    return result

def assemble(source):
    symbols = dict(PREDEFINED)
    rows = clean_lines(source)
    rom = 0
    # Pass 1: collect labels.
    for line_no, line in rows:
        if line.startswith("(") and line.endswith(")"):
            label = line[1:-1].strip()
            if not label or any(ch.isspace() for ch in label):
                raise ValueError(f"Line {line_no}: invalid label")
            if label in symbols:
                raise ValueError(f"Line {line_no}: duplicate or reserved label '{label}'")
            symbols[label] = rom
        else:
            rom += 1

    # Pass 2: translate instructions and allocate variables.
    next_variable = 16
    machine = []
    for line_no, line in rows:
        if line.startswith("(") and line.endswith(")"):
            continue
        try:
            if line.startswith("@"):
                token = line[1:].strip()
                if not token:
                    raise ValueError("missing address")
                if token.isdigit():
                    value = int(token)
                else:
                    if token not in symbols:
                        symbols[token] = next_variable
                        next_variable += 1
                    value = symbols[token]
                if not 0 <= value <= 32767:
                    raise ValueError("A-instruction address must be 0..32767")
                machine.append(f"{value:016b}")
            else:
                # Remove whitespace, then parse dest=comp;jump.
                inst = "".join(line.split())
                if inst.count("=") > 1 or inst.count(";") > 1:
                    raise ValueError("malformed C-instruction")
                if "=" in inst:
                    dest, rest = inst.split("=", 1)
                else:
                    dest, rest = "", inst
                if ";" in rest:
                    comp, jump = rest.split(";", 1)
                else:
                    comp, jump = rest, ""
                if dest not in DEST:
                    raise ValueError(f"invalid destination '{dest}'")
                if comp not in COMP:
                    raise ValueError(f"invalid computation '{comp}'")
                if jump not in JUMP:
                    raise ValueError(f"invalid jump '{jump}'")
                machine.append("111" + COMP[comp] + DEST[dest] + JUMP[jump])
        except ValueError as exc:
            # K=46; K mod 3 = 1: clear line-numbered invalid-line diagnostics.
            raise ValueError(f"Line {line_no}: invalid instruction ({exc})") from None
    return machine, symbols

def main():
    if len(sys.argv) not in (2, 3):
        print("Usage: python assembler.py input.asm [output.hack]")
        return 2
    source = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) == 3 else str(Path(source).with_suffix(".hack"))
    try:
        machine, _ = assemble(source)
        Path(output).write_text("\n".join(machine) + "\n", encoding="utf-8")
        print(f"Assembled {len(machine)} instructions -> {output}")
        return 0
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
