import sys
import os

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101",
    "!A": "0110001", "-D": "0001111", "-A": "0110011",
    "D+1": "0011111", "A+1": "0110111", "D-1": "0001110",
    "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011",
    "M+1": "1110111", "M-1": "1110010", "D+M": "1000010",
    "D-M": "1010011", "M-D": "1000111", "D&M": "1000000",
    "D|M": "1010101",
}

DEST = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111",
}

JUMP = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}

PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576,
}
for i in range(16):
    PREDEFINED["R" + str(i)] = i


def clean(line):
    if "//" in line:
        line = line[:line.index("//")]
    return "".join(line.split())


def first_pass(lines):
    symbols = dict(PREDEFINED)
    instructions = []
    rom_address = 0
    label_lines = {}
    for number, raw in enumerate(lines, start=1):
        text = clean(raw)
        if text == "":
            continue
        if text.startswith("(") and text.endswith(")"):
            label = text[1:-1]
            if label in label_lines:
                print("Warning: line " + str(number) + ": label '" + label + "' is already defined on line " + str(label_lines[label]))
            else:
                label_lines[label] = number
                symbols[label] = rom_address
            continue
        instructions.append((number, text))
        rom_address += 1
    return symbols, instructions, label_lines


def translate_c(text):
    dest = ""
    jump = ""
    comp = text
    if "=" in comp:
        dest, comp = comp.split("=", 1)
    if ";" in comp:
        comp, jump = comp.split(";", 1)
    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def second_pass(instructions, symbols):
    output = []
    next_variable = 16
    for number, text in instructions:
        if text.startswith("@"):
            name = text[1:]
            if name.isdigit():
                value = int(name)
            else:
                if name not in symbols:
                    symbols[name] = next_variable
                    next_variable += 1
                value = symbols[name]
            output.append(format(value, "016b"))
        else:
            output.append(translate_c(text))
    return output


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 assembler.py File.asm")
        sys.exit(1)
    source = sys.argv[1]
    with open(source) as handle:
        lines = handle.read().splitlines()
    symbols, instructions, label_lines = first_pass(lines)
    output = second_pass(instructions, symbols)
    target = os.path.splitext(source)[0] + ".hack"
    with open(target, "w") as handle:
        handle.write("\n".join(output) + "\n")
    print("Wrote " + target + " (" + str(len(output)) + " instructions)")


main()
