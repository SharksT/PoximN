import sys
f_input = open(sys.argv[1], 'r')
f_output = open(sys.argv[2], 'w')
memory = []
reg = [0] * 36
img = 25
for line in f_input:
    memory.append(int(line, 16))[2:].zfill(32)


def checktype(result):
    global reg
    x = 0
    y = 0
    z = 0
    t = ''
    result1 = ['add', 'sub', 'mul', 'div', 'cmp', 'shl',
               'shr', 'and', 'not', 'or', 'xor', 'push', 'pop']
    result2 = ['addi', 'subi', 'muli', 'divi', 'cmpi', 'andi', 'noti', 'ldw', 'stw',
               'ldb', 'stb', 'ldw', 'call', 'ret','xori','ori']
    result3 = ['bun', 'beq', 'blt', 'bne', 'ble', 'bge', 'int', 'bgt']
    if isinstance(reg[33], int):
        reg[33] = str(bin(reg[33]))
    if result in result1:
        if result == 'cmp':
            y = int(str(reg[33][16] + reg[33][27:32]), 2)
            x = int(str(reg[33][15] + reg[33][22:27]), 2)
            z = 0
        else:
            y = int(str(reg[33][16] + reg[33][27:32]), 2)
            x = int(str(reg[33][15] + reg[33][22:27]), 2)
            z = int(str(reg[33][17] + reg[33][18:22]), 2)
        t = 'U'
    elif result in result2:
        y = int(reg[33][27:32], 2)
        x = int(reg[33][22:27], 2)
        z = int(reg[33][6:22], 2)
        t = 'F'
    elif result in result3:
        x = int(bin(int(reg[33][14:32], 2)), 2)
        t = 'S'
    reg[33] = int(reg[33], 2)
    return {'x': x, 'y': y, 'z': z, 't': t}


while img != 0:
    reg[33] = memory[reg[32]]
    reg[0] = 0
    ir = bin(reg[33])[2:]
    op = (ir[0:6])
    choices = {'000000': 'add', '000001': 'sub', '000010': 'mul', '000011': 'div', '000100': 'cmp', '000101': 'shl',
               '000110': 'shr', '000111': 'and', '001000': 'not', '001001': 'or', '001010': 'xor', '001011': 'push',
               '001100': 'pop',
               '010000': 'addi', '010001': 'subi', '010010': 'muli', '010011': 'divi', '010100': 'cmpi',
               '010101': 'andi',
               '010110': 'noti', '010111': 'ori', '011000': 'xori', '011001': 'ldw', '011010': 'stw', '011011': 'ldb',
               '011100': 'stb',
               '100000': 'bun', '100001': 'beq', '100010': 'blt', '100011': 'bgt', '100100': 'bne', '100101': 'ble',
               '100110': 'bge', '110000': 'call', '110001': 'ret', '111111': 'int'}
    result = choices.get(op, 'Não definido')

f_input.close()
f_output.close()