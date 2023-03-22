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
inp_buffer = []
NUMBERS = "1234567890"

for l in code.split("\n"):
    for c in l:
        program.append(c)


in_string = False
in_comment = False

for i,c in enumerate(program):
    if (not in_string) and (not in_comment):
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
        if c=='|':
            stack.append(("||",i))
            in_comment = True
    elif in_string:
        if c=='"':
            stack.pop(-1)
            in_string = False
    elif in_comment:
        if c=='|':
            blocks.append(('||',stack.pop(-1)[1],i))
            in_comment = False

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

def get_return():
    global ip
    for block in blocks:
        if block[2] == ip:
            return block[1]
    print(f"No return for {ip}")
    sys.exit(1)

def get_skip():
    global ip
    for block in blocks:
        if block[1] == ip:
            return block[2]
    print(f"No skip for {ip}")
    sys.exit(1)

def arithmetic(func):
    if len(stack) < 2:
        print(f"Not enough values for arithmetic at {ip}")
        sys.exit(1)
    b = stack.pop(-1)
    a = stack.pop(-1)
    stack.append(func(a,b))

def get_input():
    global inp_buffer
    if len(inp_buffer) > 0:
        return ord(inp_buffer.pop(0))
    user_inp = input()
    inp_buffer.extend(user_inp)
    inp_buffer.append("\n")
    return get_input()

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
        elif c == '#':
            c = next_char()
            if c == 'c':
                print(chr(cells[cp]), end="")
            else:
                ip -= 1
                print(cells[cp], end="")
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
    elif c=='(':
        if not cells[cp]:
            ip = get_skip()
    elif c==')':
        if cells[cp]:
            ip = get_return()
    elif c=='[':
        if not cells[cp]:
            ip = get_skip()
    elif c==']':
        pass
    elif c=='{':
        c = next_char()
        if c == '+':
            add = lambda a, b : a+b
            arithmetic(add)
        elif c == '-':
            sub = lambda a, b : a-b
            arithmetic(sub)
        elif c == '*':
            mul = lambda a, b : a*b
            arithmetic(mul)
        elif c == '/':
            div = lambda a, b : a/b
            arithmetic(div)
        elif c == '%':
            mod = lambda a, b : a%b
            arithmetic(mod)
        elif c == '=':
            eq = lambda a, b : a==b
            arithmetic(eq)
        else:
            print(f"Invalid arithmetic '{c}' at {ip}")
            sys.exit(1)
        c = next_char()
        if c != '}':
            print("Expected '}' at " + ip)
    elif c=='.':
        c = next_char()
        if c=='#':
            cells[cp] = get_input()
        else:
            ip -= 1
            stack.append(get_input())
    elif c=='<':
        c = next_char()
        if c != '#':
            print(f"Invalid command {ip}")
            sys.exit(1)
        cp-=1
        if cp < 0: cp = len(cells)-cp
        if cp >= len(cells): cp = cp-len(cells)
    elif c=='>':
        c = next_char()
        if c != '#':
            print(f"Invalid command {ip}")
            sys.exit(1)
        cp-=1
        if cp < 0: cp = len(cells)-cp
        if cp >= len(cells): cp = cp-len(cells)
    elif c=='|':
        ip = get_skip()
    else:
        print(f"Invalid instruction '{c}' at {ip}")
        sys.exit(1)
    ip += 1