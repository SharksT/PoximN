import sys
f_input = open(sys.argv[1], 'r')
f_output = open(sys.argv[2], 'w')
rx, ry, rz, memory, reg, img, pre_pc,rt = 0, 0, 0, [], [0] * 36, 25, 0, ''
for line in f_input:
    memory.append(int(line, 16))


def calculate_fr(x, y, z, result):
    global reg,rt
    aux, h = list(str(bin(reg[35])[2:]).zfill(32)), 23
    result1 = ['div', 'mul', 'muli', 'divi']
    result2 = ['add', 'addi']
    if result == 'div' or result == 'divi':
        if z == 0:
            h = 1
        else:
            h = 0
    if rt == 'U' or rt == 'F':
        if result == 'cmp' or result == 'cmpi':
            if x == y:
                aux[31] = '1'
                aux[30] = '0'
                aux[29] = '0'
            elif x < y:
                aux[30] = '1'
                aux[29] = '0'
            elif x > y:
                aux[31] = '0'
                aux[30] = '0'
                aux[29] = '1'
            elif x != y:
                aux[31] = '0'
        else:
            if reg[rx] < 0:
                aux[27] = '1'
                reg[rx] = 0xFFFFFFFF + reg[rx]
            else:
                if abs(int(reg[rx])) < (2 ** 32):
                    aux[27] = '0'
            if abs(int(reg[rx])) > (2 ** 32):
                aux[27] = '1'
                if result in result1:
                    x = x
                else:
                    reg[rx] = reg[rx] - (2 ** 32)
            if aux[27] != '1' and result in result2:
                if abs(int(reg[rx])) < (2 ** 32):
                    aux[27] = '0'
            if h == 1:
                aux[28] = '1'
            if h == 0:
                aux[28] = '0'
    reg[35] = ''.join(aux)
    reg[35] = int(reg[35], 2)
    return reg[35]


def calculate_er(x, y, z, result):
    global reg
    if result == 'div' or result == 'divi':
        r = x
        try:
            reg[34] = y % z
        except ZeroDivisionError:
            reg[34] = '0'.zfill(32)
    else:
        x = str(bin(x))[2:].zfill(64)
        a = x[len(x) % 64:]
        reg[34] = a[:32]
        r = int(a[32:], 2)
    reg[34] = int(reg[34],2)
    return r


def checktype(result):
    global reg
    x, y, z, t = 0, 0, 0, ''
    result1 = ['add', 'sub', 'mul', 'div', 'cmp', 'shl',
               'shr', 'and', 'not', 'or', 'xor', 'push', 'pop']
    result2 = ['addi', 'subi', 'muli', 'divi', 'cmpi', 'andi', 'noti', 'ldw', 'stw',
               'ldb', 'stb', 'ldw', 'call', 'ret','xori','ori']
    result3 = ['bun', 'beq', 'blt', 'bne', 'ble', 'bge', 'int', 'bgt']
    reg[33] = str(bin(reg[33]))[2:].zfill(32)
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


def checkextra(x):

    if x == 32:
        x = 'pc'
    elif x == 33:
        x = 'ir'
    elif x == 34:
        x = 'er'
    elif x == 35:
        x = 'fr'
    else:
        x = 'r{}'.format(x)
    return x


def prints(x, y, z, result, sinal):
    lista = ['add', 'sub', 'addi', 'subi', 'mul', 'muli', 'div', 'divi', 'cmp', 'cmpi']
    if result in lista:
        calculate_fr(rx, ry, rz, result)
    global reg, pre_pc
    reg[0] = 0
    pre, mid, pos = '', '', ''
    tipo = ['add','sub','mul','div','shl','shr','and','or','xor','addi','subi','muli','divi','andi',
            'ori','xori','ldw','stw','ldb','stb','call','isr']
    er_ac, aux, fr_ac = ['mul','muli','div','divi'],'',['add', 'sub', 'addi', 'subi', 'mul', 'muli', 'div', 'divi']
    i_ac = ['muli','divi','addi','subi','ldw','ldb']
    if result in er_ac:
        aux = "ER=0x{},".format(hex(reg[34])[2:].zfill(8).upper())
    else:
        aux = ""
    if result in tipo:
        if result in i_ac:
            pre = "[0x{}]\t".format(hex(pre_pc * 4)[2:].zfill(8).upper()) + (
                "{} {},{},0x{}".format(result, checkextra(x), checkextra(y),hex(z)[2:].zfill(4).upper() )).ljust(20)
        elif result == 'stb' or result == 'stw':
            pre = "[0x{}]\t".format(hex(pre_pc * 4)[2:].zfill(8).upper()) + (
                "{} {},0x{},{}".format(result, checkextra(x), hex(z)[2:].zfill(4).upper(),checkextra(y) )).ljust(20)
        else:
            pre = "[0x{}]\t".format(hex(pre_pc*4)[2:].zfill(8).upper()) + ("{} {},{},{}".format(result, checkextra(z),
                                checkextra(x), checkextra(y))).ljust(20)
    if (result not in tipo) and (result != 'ret' and result != 'reti' and result != 'int'):
        pre = "[0x{}]\t".format(hex(pre_pc*4)[2:].zfill(8).upper()) + ("{} {},{}".format(result, checkextra(x), checkextra(y))).ljust(20)
    mid = "FR=0x{},".format(hex(reg[35])[2:].zfill(8).upper())
    if result == 'ldw':
        pos = "{}=MEM[({}+0x{})<<2]=0x{}".format(checkextra(rx).upper(),checkextra(ry),hex(rz)[2:].zfill(4).upper(),
                                                 hex(reg[rx])[2:].zfill(8).upper())
    elif result == 'ldb':
        pos = "{}=MEM[({}+0x{})<<2]=0x{}".format(checkextra(rx).upper(), checkextra(ry), hex(rz)[2:].zfill(4).upper(),
                                               hex(reg[rx])[2:].zfill(2).upper())
    elif result == 'stb':
        pos = "MEM[{}+0x{}]={}=0x{}".format(checkextra(rx), hex(rz)[2:].zfill(4).upper(),checkextra(y).upper(),
                                            hex(reg[ry])[2:].zfill(4).upper())
    elif result in i_ac:
        pos = "{}{}={}{}0x{}=0x{}".format(aux, checkextra(x).upper(), checkextra(y).upper(), sinal,
                                         hex(z)[2:].zfill(4).upper(), hex(reg[rx])[2:].zfill(8).upper())
    else:
        pos = "{}{}={}{}{}=0x{}".format(aux,checkextra(z).upper(),checkextra(x).upper(), sinal, checkextra(y).upper(),
                                     hex(reg[rz])[2:].zfill(8).upper())
    if result in fr_ac:
        return pre + mid + pos
    elif result == 'cmp' or result == 'cmpi':
        return pre + mid[:13]
    else:
        return pre + pos

def montador():
    global reg, pre_pc, rx, ry, rz,rt
    reg[0], pre_pc, r = 0, reg[32], checktype(result)
    rx, ry, rz, rt = r['x'], r['y'], r['z'], r['t']

while img != 0:
    reg[33] = memory[reg[32]]
    reg[0] = 0
    ir = bin(reg[33])[2:].zfill(32)
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

    if result == 'add':
        montador()
        reg[rz] = int(reg[rx]) + int(reg[ry])
        f_output.write(prints(rx, ry, rz, result, '+') + '\n')
        reg[32] += 1
    elif result == 'sub':
        montador()
        reg[rz] = int(reg[rx]) - int(reg[ry])
        f_output.write(prints(rx, ry, rz, result, '-')+ '\n')
        reg[32] += 1
    elif result == 'mul':
        montador()
        reg[rz] = int(reg[rx]) * int(reg[ry])
        reg[rz] = calculate_er(reg[rz], 0, 0, result)
        f_output.write(prints(rx, ry, rz, result, '*') + '\n')
        reg[32] += 1
    elif result == 'div':
        montador()
        try:
            reg[rz] = int(float(int(reg[rx]) / int(reg[ry])))
            reg[rz] = calculate_er(reg[rz], reg[rx], reg[ry], result)
            f_output.write(prints(rx, ry, rz, result, '/') + '\n')
        except ZeroDivisionError:
            reg[rz] = calculate_er(reg[rz], reg[rx], reg[ry], result)
            f_output.write(prints(rx, ry, rz, result, '/') + '\n')
        reg[32] += 1
    elif result == 'cmp':
        montador()
        reg[32] += 1
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'shl':
        montador()
        reg[rz] = reg[rx] << (ry + 1)
        reg[rz] = calculate_er(reg[rz], 0, 0, result)
        f_output.write(prints(rx, ry, rz, result, '<<') + '\n')
        reg[32] += 1
    elif result == 'shl':
        montador()
        reg[rz] = reg[rx] << (ry + 1)
        reg[rz] = calculate_er(reg[rz], 0, 0, result)
        f_output.write(prints(rx, ry, rz, result, '<<') + '\n')
        reg[32] += 1
    elif result == 'shr':
        montador()
        reg[rz] = reg[rx] >> (ry + 1)
        reg[rz] = calculate_er(reg[rz], 0, 0, result)
        f_output.write(prints(rx, ry, rz, result, '<<') + '\n')
        reg[32] += 1
    elif result == 'and':
        montador()
        reg[rz] = reg[rx] & reg[ry]
        f_output.write(prints(rx, ry, rz, result, '&') + '\n')
        reg[32] += 1
    elif result == 'not':
        montador()
        reg[rx] = 4294967295 - reg[ry]
        f_output.write(prints(rx, ry, rz, result, '~') + '\n')
        reg[32] += 1
    elif result == 'or':
        montador()
        reg[rz] = reg[rx] | reg[ry]
        f_output.write(prints(rx, ry, rz, result, '|') + '\n')
        reg[32] += 1
    elif result == 'xor':
        montador()
        reg[rz] = reg[rx] ^ reg[ry]
        f_output.write(prints(rx, ry, rz, result, '^') + '\n')
        reg[32] += 1
    elif result == 'push':
        montador()
        memory[int(reg[rx])] = reg[ry]
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
        reg[rx] = reg[rx] - 1
        reg[32] += 1
    elif result == 'pop':
        montador()
        reg[ry] = reg[ry] + 1
        reg[rx] = memory[reg[ry]]
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
        reg[rx] = reg[rx] - 1
        reg[32] += 1
    elif result == 'addi':
        montador()
        reg[rx] = int(reg[ry]) + rz
        f_output.write(prints(rx, ry, rz, result, '+') + '\n')
        reg[32] += 1
    elif result == 'subi':
        montador()
        reg[rx] = int(reg[ry]) - rz
        f_output.write(prints(rx, ry, rz, result, '-') + '\n')
        reg[32] += 1
    elif result == 'muli':
        montador()
        reg[rx] = int(reg[ry]) * rz
        reg[rx] = calculate_er(reg[rx], 0, 0, result)
        f_output.write(prints(rx, ry, rz, result, '*') + '\n')
        reg[32] += 1
    elif result == 'divi':
        montador()
        try:
            reg[rx] = int(float(int(reg[ry]) / int(rz)))
            reg[rx] = calculate_er(rx, reg[ry], rz, result)
            f_output.write(prints(rx, ry, rz, result, '/') + '\n')
        except ZeroDivisionError:
            reg[rx] = calculate_er(rx, reg[ry], rz, result)
            f_output.write(prints(rx, ry, rz, result, '/') + '\n')
        reg[32] += 1
    elif result == 'cmpi':
        montador()
        reg[32] += 1
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'andi':
        montador()
        reg[rx] = int(reg[ry]) & rz
        f_output.write(prints(rx, ry, rz, result, '&') + '\n')
        reg[32] += 1
    elif result == 'noti':
        montador()
        reg[rx] = 4294967295 - rz
        f_output.write(prints(rx, ry, rz, result, '~') + '\n')
        reg[32] += 1
    elif result == 'ori':
        montador()
        reg[rx] = reg[ry] | rz
        f_output.write(prints(rx, ry, rz, result, '|') + '\n')
        reg[32] += 1
    elif result == 'xori':
        montador()
        reg[rx] = reg[ry] ^ rz
        f_output.write(prints(rx, ry, rz, result, '^') + '\n')
        reg[32] += 1
    elif result == 'ldw':
        montador()
        reg[rx] = int(memory[int(reg[ry] + rz)])
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
        reg[32] += 1
    elif result == 'sdw':
        montador()
        memory[int(reg[rx]) + rz] = reg[ry]
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
        reg[32] += 1
    elif result == 'ldb':
        montador()
        reg[rx] = bin(memory[int((reg[ry] + rz) / 4)])[2:].zfill(32)
        if ((reg[ry] + rz) % 4) == 0:
            reg[rx] = int(reg[rx][0:8], 2)
        elif ((reg[ry] + rz) % 4) == 1:
            reg[rx] = int(reg[rx][8:16], 2)
        elif ((reg[ry] + rz) % 4) == 2:
            reg[rx] = int(reg[rx][16:24], 2)
        elif ((reg[ry] + rz) % 4) == 3:
            reg[rx] = int(reg[rx][24:32], 2)
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
        reg[32] += 1
    elif result == 'stb':
        montador()
        a = int((reg[rx] + rz) / 4)
        reg[ry] = str(bin(reg[ry])[2:].zfill(32))
        if ((reg[rx] + rz) % 4) == 3:
            memory[a] = int(reg[ry][0:8], 2)
        elif ((reg[rx] + rz) % 4) == 2:
            memory[a] = int(reg[ry][8:16], 2)
        elif ((reg[rx] + rz) % 4) == 1:
            memory[a] = int(reg[ry][16:24], 2)
        elif ((reg[rx] + rz) % 4) == 0:
            memory[a] = int(reg[ry][24:32], 2)
        reg[ry] = int(reg[ry],2)
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
        reg[32] += 1
    elif result == 'bun':
        montador()
        reg[32] = rx
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'int':
        montador()
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
        if rz == 0:
            reg[0] = 0
            f_output.write('[END OF SIMULATION]')
            break
    else:
        f_output.write('Nao definido')

f_input.close()
f_output.close()