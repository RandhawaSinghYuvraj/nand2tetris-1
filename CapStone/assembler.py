import os
import sys

COMP = {
    "0":   "0101010",
    "1":   "0111111",
    "-1":  "0111010",
    "D":   "0001100",
    "A":   "0110000",
    "!D":  "0001101",
    "!A":  "0110001",
    "-D":  "0001111",
    "-A":  "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M":   "1110000",
    "!M":  "1110001",
    "-M":  "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101",
}

DEST = {
    "":    "000",
    "M":   "001",
    "D":   "010",
    "MD":  "011",
    "A":   "100",
    "AM":  "101",
    "AD":  "110",
    "AMD": "111",
}

JUMP = {
    "":    "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}


def init_symbols() -> dict[str, int]:
    symbols = {
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4,
        "SCREEN": 16384,
        "KBD": 24576,
    }
    for i in range(16):
        symbols[f"R{i}"] = i
    return symbols


def clean_line(raw: str) -> str:
    return raw.split("//", 1)[0].strip()


def assemble(asm_path: str, hack_path: str) -> None:
    with open(asm_path, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    symbols = init_symbols()
    seen_labels: set[str] = set()
    instructions: list[str] = []

    rom_address = 0
    for line_num, raw in enumerate(raw_lines, start=1):
        line = clean_line(raw)
        if not line:
            continue

        if line.startswith("(") and line.endswith(")"):
            label = line[1:-1].strip()
            if label in seen_labels:
                print(
                    f"Warning (Line {line_num}): Duplicate label '({label})' written twice; "
                    f"keeping first address {symbols[label]}."
                )
            else:
                seen_labels.add(label)
                symbols[label] = rom_address
        else:
            instructions.append(line)
            rom_address += 1

    # Second pass: translate instructions to 16-bit binary strings
    next_var_addr = 16
    output_lines: list[str] = []

    for inst in instructions:
        if inst.startswith("@"):
            symbol = inst[1:]
            if symbol.isdigit():
                value = int(symbol)
            else:
                if symbol not in symbols:
                    symbols[symbol] = next_var_addr
                    next_var_addr += 1
                value = symbols[symbol]
            output_lines.append(f"{value:016b}")
        else:
            dest_part = ""
            jump_part = ""
            comp_part = inst

            if "=" in comp_part:
                dest_part, comp_part = comp_part.split("=", 1)
            if ";" in comp_part:
                comp_part, jump_part = comp_part.split(";", 1)

            dest_part = dest_part.strip()
            comp_part = comp_part.strip()
            jump_part = jump_part.strip()

            binary = "111" + COMP[comp_part] + DEST[dest_part] + JUMP[jump_part]
            output_lines.append(binary)

    with open(hack_path, "w", encoding="utf-8") as f:
        for line in output_lines:
            f.write(line + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 assembler.py <input.asm> [output.hack]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = (
        sys.argv[2]
        if len(sys.argv) >= 3
        else os.path.splitext(input_file)[0] + ".hack"
    )
    assemble(input_file, output_file)
