import sys

COMP = {
 '0':'0101010','1':'0111111','-1':'0111010','D':'0001100','A':'0110000',
 '!D':'0001101','!A':'0110001','-D':'0001111','-A':'0110011','D+1':'0011111',
 'A+1':'0110111','D-1':'0001110','A-1':'0110010','D+A':'0000010','A+D':'0000010',
 'D-A':'0010011','A-D':'0000111','D&A':'0000000','A&D':'0000000',
 'D|A':'0010101','A|D':'0010101',
 'M':'1110000','!M':'1110001','-M':'1110011','M+1':'1110111','M-1':'1110010',
 'D+M':'1000010','M+D':'1000010','D-M':'1010011','M-D':'1000111',
 'D&M':'1000000','M&D':'1000000','D|M':'1010101','M|D':'1010101'}
JUMP = {'':'000','JGT':'001','JEQ':'010','JGE':'011','JLT':'100','JNE':'101','JLE':'110','JMP':'111'}

def dest_bits(d):
    if any(c not in 'ADM' for c in d) or len(set(d)) != len(d):
        raise ValueError(f"invalid destination '{d}'")
    return ('1' if 'A' in d else '0') + ('1' if 'D' in d else '0') + ('1' if 'M' in d else '0')

def clean(line):
    return line.split('//')[0].replace(' ', '').replace('\t', '').strip()

def assemble(path):
    symbols = {f'R{i}': i for i in range(16)}
    symbols.update({'SP':0,'LCL':1,'ARG':2,'THIS':3,'THAT':4,'SCREEN':16384,'KBD':24576})

    lines = []                          # (source line number, instruction)
    with open(path) as f:
        for n, raw in enumerate(f, 1):
            c = clean(raw)
            if c:
                lines.append((n, c))

    # ---- Pass 1: record labels ----
    pc, instrs = 0, []
    for n, c in lines:
        if c.startswith('(') and c.endswith(')'):
            symbols[c[1:-1]] = pc
        else:
            instrs.append((n, c))
            pc += 1

    # ---- Pass 2: translate (with error reporting) ----
    out, next_var, errors = [], 16, 0
    for n, c in instrs:
        try:
            if c[0] == '@':
                v = c[1:]
                if not v:
                    raise ValueError("empty A-instruction")
                if v.isdigit():
                    addr = int(v)
                else:
                    if v not in symbols:
                        symbols[v] = next_var
                        next_var += 1
                    addr = symbols[v]
                if addr > 32767:
                    raise ValueError("address out of range")
                out.append(format(addr, '016b'))
            else:
                dest, jmp = '', ''
                if '=' in c:
                    dest, c = c.split('=', 1)
                if ';' in c:
                    c, jmp = c.split(';', 1)
                if c not in COMP:
                    raise ValueError(f"invalid computation '{c}'")
                if jmp not in JUMP:
                    raise ValueError(f"invalid jump '{jmp}'")
                out.append('111' + COMP[c] + dest_bits(dest) + JUMP[jmp])
        except ValueError as e:
            print(f"Line {n}: invalid instruction - {e}")
            errors += 1

    if errors:
        sys.exit(f"{errors} error(s) found; no .hack file written.")

    hack = path.rsplit('.', 1)[0] + '.hack'
    with open(hack, 'w') as f:
        f.write('\n'.join(out) + '\n')
    print(f"Wrote {hack}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("Usage: python assembler.py File.asm")
    assemble(sys.argv[1])