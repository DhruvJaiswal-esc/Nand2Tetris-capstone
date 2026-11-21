// Box.asm  -  K = 64
// Start row = 64  -> address 16384 + 32*64 = 18432
// Height = 20 rows
// Width  = 16 * ((64 mod 4) + 1) = 16 pixels = 1 word per row
// Draws a black box while any key is pressed, erases it when released.

(LOOP)
    @KBD
    D=M
    @DRAW
    D;JNE           // key pressed -> draw
    @color
    M=0             // no key -> color = white (erase)
    @FILL
    0;JMP
(DRAW)
    @color
    M=-1            // key pressed -> color = black
(FILL)
    @18432          // 16384 + 32*64
    D=A
    @addr
    M=D             // addr = first word of the current row
    @20             // box height
    D=A
    @rows
    M=D             // rows = 20
(ROWLOOP)
    @1              // width in words = (64 mod 4) + 1
    D=A
    @cols
    M=D             // cols = 1
    @addr
    D=M
    @p
    M=D             // p = addr
(COLLOOP)
    @color
    D=M
    @p
    A=M
    M=D             // RAM[p] = color
    @p
    M=M+1           // next word in this row
    @cols
    M=M-1
    D=M
    @COLLOOP
    D;JGT           // more words in this row?
    @32
    D=A
    @addr
    M=M+D           // addr += 32 (next screen row)
    @rows
    M=M-1
    D=M
    @ROWLOOP
    D;JGT           // more rows?
    @LOOP
    0;JMP           // go back and check keyboard
