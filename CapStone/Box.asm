// Box.asm
// Personal number K = 77
// Start row = 77 -> SCREEN (16384) + 32 * 77 = 18848
// Height = 20 rows, Width = 16 * ((77 mod 4) + 1) = 32 pixels (2 words per row)

(LOOP)
    @KBD
    D=M             // Read keyboard memory map
    @PRESSED
    D;JNE           // Jump to PRESSED if any key is held (D != 0)

    @color
    M=0             // Key released: white (0)
    @DRAW
    0;JMP

(PRESSED)
    @color
    M=-1            // Key pressed: black (-1 = 0xFFFF)

(DRAW)
    @18848          // Starting address: row 77, column 0
    D=A
    @addr
    M=D

    @20             // Box height: 20 rows
    D=A
    @count
    M=D

(ROW)
    @color
    D=M
    @addr
    A=M
    M=D             // Fill word 0 (pixels 0..15)
    A=A+1
    M=D             // Fill word 1 (pixels 16..31)

    @32
    D=A
    @addr
    M=D+M           // Advance addr to the next screen row (+32 words)

    @count
    MD=M-1          // Decrement remaining rows
    @ROW
    D;JGT           // Continue until all 20 rows are drawn

    @LOOP
    0;JMP           // Poll keyboard again
