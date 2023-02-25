import sys
import os

if len(sys.argv) != 2:
    print("Usage: keyboardcat.py <filename>")
    sys.exit(1)

if not os.path.exists(sys.argv[1]):
    print(sys.argv[1] + " does not exist")
    sys.exit(1)

if not os.path.isfile(sys.argv[1]):
    print(sys.argv[1] + " is not a file")
    sys.exit(1)

with open(sys.argv[1]) as f:
    code = f.read()

stack = []
cells = [0]*4096 # 4 KB
program = []
blocks = []
ip = 0
cp = 0
NUMBERS = "1234567890"

for l in code.split("\n"):
    for c in l:
        program.append(c)


in_string = False

for i,c in enumerate(program):
    if not in_string:
        if c=='[':
            stack.append(('[]',i))
        if c==']':
            if stack[-1][0] != '[]':
                print(f"Unmatched ']' at {i}")
                sys.exit(1)
            else:
                start = stack.pop(-1)
                blocks.append(('[]',start[1],i))
        if c=='(':
            stack.append(('()',i))
        if c==')':
            if stack[-1][0] != '()':
                print(f"Unmatched ')' at {i}")
                sys.exit(1)
            else:
                start = stack.pop(-1)
                blocks.append(('()',start[1],i))
        if c=='{':
            stack.append(('{}',i))
        if c=='}':
            if stack[-1][0] != '{}':
                print("Unmatched '}' at "+i)
                sys.exit(1)
            else:
                start = stack.pop(-1)
                blocks.append(('{}',start[1],i))
        if c=='"':
            stack.append(('"',i))
            in_string = True
    else:
        if c=='"':
            stack.pop(-1)
            in_string = False

if len(stack) > 0:
    while len(stack) > 0:
        print(f"Unmatched '{stack[-1][0][0]}' at {stack.pop(-1)[1]}")
    sys.exit(1)

def next_char():
    global ip
    ip += 1
    if ip >= len(program):
        return 0
    return program[ip]

def parse_number():
    global ip
    num = ""
    c = next_char()
    while c in NUMBERS:
        num = num + str(c)
        c = next_char()
        if not c: break
    ip -= 1
    if len(num) == 0:
        print("Please supply a number")
        sys.exit(1)
    return int(num)

while True:
    if ip >= len(program):
        break
    c = program[ip]
    if c == '$':
        c = next_char()
        if c == '"':
            c = next_char()
            while c != '"':
                print(c,end="")
                c = next_char()
            print()
        elif c == '#':
            c = next_char()
            if c == 'c':
                print(chr(cells[cp]))
            else:
                ip -= 1
                print(cells[cp])
        else:
            print(f"Invalid instruction '{c}' at {ip}")
            sys.exit(1)
    elif c=='#':
        cells[cp] = parse_number()
    elif c=='P':
        c = next_char()
        if c == '#':
            stack.append(cells[cp])
        elif c == 'n':
            stack.append(parse_number())
        else:
            print(f"Invalid instruction at {ip}")
    elif c=='p':
        if len(stack) == 0:
            print("Error nothing to pop")
            sys.exit(1)
        cells[cp] = stack.pop(-1)
    else:
        print(f"Invalid instruction '{c}' at {ip}")
        sys.exit(1)
    ip += 1