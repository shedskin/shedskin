# bfi - BrainFuck GNU interpreter, (C) 2002 Philippe Biondi, biondi@cartel-securite.fr
# Modified for ShedSkin, but can be used with Python/Psyco too

from sys import stdin, stdout, argv

def BF_interpreter(prog):
    CELL = 255 # Or 65535  default 255
    # clear program to speed up execution
    prog = "".join([c for c in prog if c in "><+-.,[]"])
    len_prog = len(prog)

    tape = [0] # This can be initialized to 30000 cells
    ip = 0
    p = 0
    level = 0

    while ip < len_prog:
        x = prog[ip]
        ip += 1

        if x == '+':
            tape[p] = (tape[p]+1) & CELL
        elif x == '-':
            tape[p] = (tape[p]-1) & CELL
        elif x == '>':
            p += 1
            if len(tape) <= p:
                tape.append(0)
        elif x == '<':
            if p:
                p -= 1
            else:
                #print "Warning: inserting one element at the begining"
                tape.insert(0, 0)
        elif x == '.':
            stdout.write( chr(tape[p]) )
        elif x == ',':
            tape[p] = ord(stdin.read(1))
        elif x == '[':
            if not tape[p]:
                while True:
                    if prog[ip] == '[':
                        level += 1
                    if prog[ip] == ']':
                        if level:
                            level -= 1
                        else:
                            break
                    ip += 1
                ip += 1
        elif x == ']':
            ip -= 2
            while True:
                if prog[ip] == ']':
                    level += 1
                if prog[ip] == '[':
                    if level:
                        level -= 1
                    else:
                        break
                ip -= 1

program = file('testdata/99bottles.bf').read()
BF_interpreter(program)
