// Nand2Tetris Capstone - K = 46
// Box: starts at screen row 46, 20 rows tall, 48 pixels wide (3 words).
// While any key is pressed, draw black; otherwise clear the same rectangle.

(START)
    @KBD
    D=M
    @DRAW
    D;JNE

// No key: clear 20 rows x 3 words.
    @17856       // SCREEN + 32*46: start at row 46
    D=A
    @ptr
    M=D
    @20
    D=A
    @rows
    M=D
(CLEAR_ROW)
    @ptr
    A=M
    M=0
    @ptr
    D=M
    @1
    A=D+A
    M=0
    @ptr
    D=M
    @2
    A=D+A
    M=0
    @ptr
    D=M
    @32
    D=D+A
    @ptr
    M=D
    @rows
    MD=M-1
    @CLEAR_ROW
    D;JGT
    @START
    0;JMP

(DRAW)
// Draw black in the same 20 x 48 pixel rectangle.
    @17856       // SCREEN + 32*46: start at row 46
    D=A
    @ptr
    M=D
    @20
    D=A
    @rows
    M=D
(DRAW_ROW)
    @ptr
    A=M
    M=-1
    @ptr
    D=M
    @1
    A=D+A
    M=-1
    @ptr
    D=M
    @2
    A=D+A
    M=-1
    @ptr
    D=M
    @32
    D=D+A
    @ptr
    M=D
    @rows
    MD=M-1
    @DRAW_ROW
    D;JGT
    @START
    0;JMP
