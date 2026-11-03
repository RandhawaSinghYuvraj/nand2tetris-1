import sys

DEST = {
    "null": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111"
}

JUMP = {
    "null": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
}

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010", "D": "0001100",
    "A": "0110000", "!D": "0001101", "!A": "0110001", "-D": "0001111",
    "-A": "0110011", "D+1": "0011111", "A+1": "0110111", "D-1": "0001110",
    "A-1": "0110010", "D+A": "0000010", "D-A": "0010011", "A-D": "0000111",
    "D&A": "0000000", "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101"
}

def clean_lines(raw_lines):
    cleaned = []
    for line_num, line in enumerate(raw_lines, 1):
        line = line.split("//")[0].strip()
        if line:
            cleaned.append((line_num, line))
    return cleaned

def first_pass(cleaned_lines):
    symbol_table = {
        "R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5, "R6": 6, "R7": 7,
        "R8": 8, "R9": 9, "R10": 10, "R11": 11, "R12": 12, "R13": 13, "R14": 14, "R15": 15,
        "SCREEN": 16384, "KBD": 24576, "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4
    }
    code_lines = []
    pc = 0
    for line_num, line in cleaned_lines:
        if line.startswith("(") and line.endswith(")"):
            symbol_table[line[1:-1]] = pc
        else:
            code_lines.append((line_num, line))
            pc += 1
    return symbol_table, code_lines

def translate_instruction(line_num, line, symbol_table, next_var_address):
    if line.startswith("@"):
        val_str = line[1:]
        if val_str.isdigit():
            val = int(val_str)
        else:
            if val_str not in symbol_table:
                symbol_table[val_str] = next_var_address
                next_var_address += 1
            val = symbol_table[val_str]
        return format(val, '016b'), next_var_address
    else:
        dest = "null"
        jump = "null"
        comp = line
        if "=" in line:
            parts = line.split("=")
            dest = parts[0].strip()
            comp = parts[1].strip()
        if ";" in comp:
            parts = comp.split(";")
            comp = parts[0].strip()
            jump = parts[1].strip()
        if comp not in COMP or dest not in DEST or jump not in JUMP:
            print(f"Line {line_num}: invalid instruction")
            sys.exit(1)
        return "111" + COMP[comp] + DEST[dest] + JUMP[jump], next_var_address

def assemble(filepath):
    with open(filepath, "r") as f:
        raw_lines = f.readlines()
    cleaned = clean_lines(raw_lines)
    symbol_table, code_lines = first_pass(cleaned)
    next_var_address = 16
    binary_lines = []
    for line_num, line in code_lines:
        bin_line, next_var_address = translate_instruction(line_num, line, symbol_table, next_var_address)
        binary_lines.append(bin_line)
    out_path = filepath.replace(".asm", ".hack")
    with open(out_path, "w") as f:
        f.write("\n".join(binary_lines) + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        assemble(sys.argv[1])
    else:
        print("Usage: python assembler.py filename.asm")
