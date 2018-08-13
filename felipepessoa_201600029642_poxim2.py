import sys
import ctypes
import math
f_input = open(sys.argv[1], 'r')
f_output = open(sys.argv[2], 'w')
rx, ry, rz, memory, reg, img, pre_pc, rt, inter_ac, watch_ac, watch_c = 0, 0, 0, {}, [0] * 38, 25, 0, '', False, False, 0
float_c, float_ac, memory[8704], memory[8705], memory[8706], memory[8707] = 0, False, 0, 0, 0, 0
float_x, float_y, float_z, terminal, terminal_ac, ie, ov = 0.0 ,0.0 ,0.0 , '', False, False, False
inter_over,soft_ac= False, False
memory[8738] = 0
float_x_ac, float_y_ac = False, False
for i, line in enumerate(f_input):
    memory[i] = int(line, 16)


def float_bin(x):
    return str(bin(ctypes.c_uint.from_buffer(ctypes.c_float(x)).value)[2:].zfill(32))


def float_expo(value1, value2):
    global float_c
    float_c = abs(int(value1[1:9], 2) - int(value2[1:9], 2)) + 2


def calculate_fr(x, y, z, result):
    # 6 IE, 5 IV, 4 OV. 3 ZD, 2 GT, 1 LT, EQ
    # 31 EQ, 30 LT, 29 GT. 28 ZD, 27 OV, 26 IV, 25 IE <- Ordem no registrador
    global reg, rt, inter_ac, ie, ov, soft_ac
    aux, h = list(str(bin(reg[35])[2:]).zfill(32)), 23
    result1 = ['div', 'mul', 'muli', 'divi']
    result2 = ['add', 'addi']
    if aux[25] == '1':
        ie = True
    if result == 'div' or result == 'divi':
        if y == 0:
            h = 1
            if aux[25] == '1':
                reg[36] = 1
                inter_ac = True
                reg[37] = reg[32] + 1
                #soft_ac = True
                reg[32] = 2
        else:
            h = 0
    if rt == 'U' or rt == 'F':
        if result == 'cmp':
            if reg[x] == reg[y]:
                aux[31] = '1'
                aux[30] = '0'
                aux[29] = '0'
            elif reg[x] < reg[y]:
                aux[31] = '0'
                aux[30] = '1'
                aux[29] = '0'
            elif reg[x] > reg[y]:
                aux[31] = '0'
                aux[30] = '0'
                aux[29] = '1'
            elif reg[x] != reg[y]:
                aux[31] = '0'
        elif result == 'cmpi':
            if reg[rx] == z:
                aux[31] = '1'
                aux[30] = '0'
                aux[29] = '0'
            elif reg[rx] < z:
                aux[31] = '0'
                aux[30] = '1'
                aux[29] = '0'
            elif reg[rx] > z:
                aux[31] = '0'
                aux[30] = '0'
                aux[29] = '1'
            elif reg[rx] != z:
                aux[31] = '0'
        else:
            if reg[rx] < 0:
                aux[27] = '1'
                reg[rx] = 0xFFFFFFFF + 1 + reg[rx]
            else:
                if abs(int(reg[rx])) < (2 ** 32):
                    aux[27] = '0'
            if abs(int(reg[rx])) > (2 ** 32):
                aux[27] = '1'
                if result in result1:
                    x = x
                else:
                    reg[rx] = reg[rx] - 0xFFFFFFFF
            if aux[27] != '1' and result in result2:
                if abs(int(reg[rx])) < (2 ** 32):
                    aux[27] = '0'
            if ov:
                aux[27] = '1'
                ov = False
            if h == 1:
                aux[28] = '1'
            if h == 0:
                aux[28] = '0'
    reg[35] = ''.join(aux)
    reg[35] = int(reg[35], 2)
    return reg[35]


def calculate_er(x, y, z, result):
    global reg, ov
    if result == 'div' or result == 'divi':
        r = x
        try:
            if result == 'divi':
                reg[34] = y % z
            elif result == 'div':
                reg[34] = x % y
        except ZeroDivisionError:
            reg[34] = 0
    else:
        x = str(bin(x))[2:].zfill(64)
        aux2 = x[len(x) % 64:]
        reg[34] = int(aux2[:32], 2)
        r = int(aux2[32:], 2)
        if ((result == 'mul') or (result == 'muli')) and (reg[34] > 0):
            ov = True
    return r


def checktype(result):
    global reg
    x, y, z, t = 0, 0, 0, ''
    result1 = ['add', 'sub', 'mul', 'div', 'cmp', 'shl',
               'shr', 'and', 'not', 'or', 'xor', 'push', 'pop']
    result2 = ['addi', 'subi', 'muli', 'divi', 'cmpi', 'andi', 'noti', 'ldw', 'stw',
               'ldb', 'stb', 'ldw', 'call', 'ret','xori','ori','isr', 'reti']
    result3 = ['bun', 'beq', 'blt', 'bne', 'ble', 'bge', 'bgt','bzd','bnz','biv','bni', 'int']
    reg[33] = str(bin(reg[33]))[2:].zfill(32)
    if result in result1:
        if result == 'cmp':
            y = int(str(reg[33][16] + reg[33][27:32]), 2)
            x = int(str(reg[33][15] + reg[33][22:27]), 2)
            z = 0
        else:
            y = int(str(reg[33][16] + reg[33][27:32]), 2)
            x = int(str(reg[33][15] + reg[33][22:27]), 2)
            z = int(str(reg[33][14] + reg[33][17:22]), 2)
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
    elif x == 36:
        x = 'cr'
    elif x == 37:
        x = 'ipc'
    else:
        x = 'r{}'.format(x)
    return x


def prints(x, y, z, result, sinal):
    lista = ['add', 'sub', 'addi', 'subi', 'mul', 'muli', 'div', 'divi', 'cmp', 'cmpi']
    if result in lista:
        calculate_fr(rx, ry, rz, result)
    global reg, pre_pc, inter_ac
    reg[0] = 0
    pre, mid, pos = '', '', ''
    tipo = ['add','sub','mul','div','shl','shr','and','or','xor','addi','subi','muli','divi','andi',
            'ori','xori','ldw','stw','ldb','stb','call','isr']
    bgs = ['bun','bgt','bne','blt','beq','ble','bzd','bnz','biv','bni','bge']
    rxry = ['push','pop','not']
    er_ac, aux, fr_ac = ['mul','muli','div','divi','shr','shl'],'',['add', 'sub', 'addi', 'subi', 'mul', 'muli', 'div', 'divi']
    i_ac = ['muli','divi','addi','subi','andi','noti','ori','xori']
    if result in er_ac:
        aux = "ER=0x{},".format(hex(reg[34])[2:].zfill(8).upper())
    else:
        aux = ""
    if result in tipo:
        if result in i_ac:
            pre = "[0x{}]\t".format(hex(pre_pc * 4)[2:].zfill(8).upper()) + (
                "{} {},{},{}".format(result, checkextra(x), checkextra(y), z)).ljust(20)
        elif (result == 'stb') or (result == 'stw'):
            pre = "[0x{}]\t".format(hex(pre_pc * 4)[2:].zfill(8).upper()) + (
                "{} {},0x{},{}".format(result, checkextra(x), hex(z)[2:].zfill(4).upper(),checkextra(y) )).ljust(20)
        elif (result == 'ldw') or (result == 'call') or (result == 'isr'):
            pre = "[0x{}]\t".format(hex(pre_pc * 4)[2:].zfill(8).upper()) + (
                "{} {},{},0x{}".format(result, checkextra(x), checkextra(y), hex(z)[2:].zfill(4).upper())).ljust(20)
        elif result == 'ldb':
            pre = "[0x{}]\t".format(hex(pre_pc * 4)[2:].zfill(8).upper()) + (
            "{} {},{},0x{}".format(result, checkextra(x), checkextra(y), hex(z)[2:].zfill(4).upper())).ljust(20)
        else:
            pre = "[0x{}]\t".format(hex(pre_pc*4)[2:].zfill(8).upper()) + ("{} {},{},{}".format(result, checkextra(z),
                                checkextra(x), checkextra(y) if (result != 'shl' and result != 'shr') else ry)).ljust(20)
    elif (result not in tipo) and (result != 'ret' and result != 'reti' and result != 'int' and result != 'cmp') and (result not in bgs) and (result not in rxry):
        pre = "[0x{}]\t".format(hex(pre_pc*4)[2:].zfill(8).upper()) + ("{} {},{}".format(result, checkextra(x),
                                                                                         z)).ljust(20)
    elif result == 'cmp' or result == 'cmpi':
        pre = "[0x{}]\t".format(hex(pre_pc * 4)[2:].zfill(8).upper()) + ("{} {},{}".format(result, checkextra(x),
                                                                                           checkextra(y))).ljust(20)
    elif result in rxry:
        pre = "[0x{}]\t".format(hex(pre_pc * 4)[2:].zfill(8).upper()) + (
            "{} {},{}".format(result, checkextra(rx), checkextra(ry))).ljust(20)
    elif result in bgs:
        pre = "[0x{}]\t".format(hex(pre_pc * 4)[2:].zfill(8).upper()) + (
            "{} 0x{}".format(result, hex(x)[2:].zfill(8).upper())).ljust(20)
    elif (result == 'ret') or (result == 'reti'):
        pre = "[0x{}]\t".format(hex(pre_pc * 4)[2:].zfill(8).upper()) + (
            "{} {}".format(result, checkextra(rx))).ljust(20)
    elif result == 'int':
        pre = "[0x{}]\t".format(hex(pre_pc * 4)[2:].zfill(8).upper()) + (
            "{} {}".format(result, rx)).ljust(20)
    mid = "FR=0x{},".format(hex(reg[35])[2:].zfill(8).upper())
    # Sessão POS
    if result == 'not':
        pos = "{}={}{}=0x{}".format(checkextra(x).upper(), sinal, checkextra(y).upper(),
                                    hex(reg[rx])[2:].zfill(8).upper())
    elif result == 'noti':
        pos = "{}={}0x{}=0x{}".format(checkextra(x).upper(), sinal,
                                          hex(z)[2:].zfill(4).upper(), hex(reg[rx])[2:].zfill(8).upper())
    elif result == 'ldw':
        pos = "{}=MEM[({}+0x{})<<2]=0x{}".format(checkextra(rx).upper(), checkextra(ry).upper(), hex(rz)[2:].zfill(4).upper(),
                                                 hex(reg[rx])[2:].zfill(8).upper())
    elif result == 'ldb':
        pos = "{}=MEM[{}+0x{}]=0x{}".format(checkextra(rx).upper(), checkextra(ry).upper(), hex(rz)[2:].zfill(4).upper(),
                                               hex(reg[rx])[2:].zfill(2).upper())
    elif result == 'stb':
        a = int((reg[rx] + rz) / 4)
        pos = "MEM[{}+0x{}]={}=0x{}".format(checkextra(rx).upper(), hex(rz)[2:].zfill(4).upper(),checkextra(y).upper(),
                                            hex(reg[ry])[2:].zfill(2).upper())
    elif result == 'stw':
        pos = "MEM[({}+0x{})<<2]={}=0x{}".format(checkextra(rx).upper(), hex(rz)[2:].zfill(4).upper(),checkextra(y).upper(),
                                                 hex(reg[ry])[2:].zfill(8).upper())
    elif result == 'call':
        pos = "{}=(PC+4)>>2=0x{},PC=({}+0x{})<<2=0x{}".format(checkextra(rx).upper(), hex(reg[rx])[2:].zfill(8).upper(),
                                                              checkextra(ry).upper(), hex(rz)[2:].zfill(4).upper(),
                                                              hex(reg[32]*4)[2:].zfill(8).upper())
    elif result == 'isr':
        pos = "{}=IPC>>2=0x{},{}=CR=0x{},PC=0x{}".format(checkextra(rx).upper(), hex(reg[rx])[2:].zfill(8).upper(),
                                                         checkextra(ry).upper(), hex(reg[ry])[2:].zfill(8).upper(),
                                                         hex(reg[32]*4)[2:].zfill(8).upper())
    elif (result == 'ret') or (result == 'reti'):
        pos = "PC={}<<2=0x{}".format(checkextra(rx).upper(), hex(reg[32]*4)[2:].zfill(8).upper())
    elif result == 'push':
        pos = "MEM[{}->0x{}]={}=0x{}".format(checkextra(rx).upper(), hex(reg[rx]*4)[2:].zfill(8).upper(),
                                             checkextra(ry).upper(), hex(reg[ry])[2:].zfill(8).upper())
    elif result == 'pop':
        pos = "{}=MEM[{}->0x{}]=0x{}".format(checkextra(rx).upper(),checkextra(ry).upper(), hex(reg[ry]*4)[2:].zfill(8).upper(),
                                                         hex(reg[rx])[2:].zfill(8).upper())
    elif result in i_ac:
        pos = "{}{}={}{}0x{}=0x{}".format(aux, checkextra(x).upper(), checkextra(y).upper(), sinal,
                                         hex(z)[2:].zfill(4).upper(), hex(reg[rx])[2:].zfill(8).upper())
    elif result == 'int':
        pos = "CR=0x{},PC=0x{}".format(hex(reg[36])[2:].zfill(8).upper(),hex(reg[32]*4)[2:].zfill(8).upper())
    elif result != 'cmp' and result != 'cmpi':
        pos = "{}{}={}{}{}=0x{}".format(aux,checkextra(z).upper(),checkextra(x).upper(), sinal,
                                        checkextra(y).upper() if (result != 'shl' and result != 'shr') else ry+1,
                                     hex(reg[rz])[2:].zfill(8).upper())
    if inter_ac:
        pos = pos + ("\n[SOFTWARE INTERRUPTION]")
        inter_ac= False
    if result in fr_ac:
        return pre + mid + pos
    elif result == 'cmp' or result == 'cmpi':
        return pre + mid[:13]
    elif result in bgs:
        return pre + "PC=0x{}".format(hex(reg[32]*4)[2:].zfill(8).upper())
    else:
        return pre + pos

def montador():
    global reg, pre_pc, rx, ry, rz, rt
    reg[0], pre_pc, r = 0, reg[32], checktype(result)
    rx, ry, rz, rt = r['x'], r['y'], r['z'], r['t']


f_output.write('[START OF SIMULATION]\n')
while img != 0:
    if bin(reg[35])[2:].zfill(32)[25] == '1':
        ie = True
    if watch_ac and (watch_c == 0) and (soft_ac is False) and ie:
        watch_ac = False
        f_output.write("[HARDWARE INTERRUPTION 1]\n")
        reg[32] = 1
        reg[36] = 3786147034
        reg[37] = pre_pc + 1
    elif float_ac and (float_c == 0)  and inter_over:
        float_ac = False
        f_output.write("[HARDWARE INTERRUPTION 2]\n")
        reg[37] = reg[32]
        reg[32] = 2
        reg[36] = 32434004
    reg[33] = memory[reg[32]]
    reg[0] = 0
    ir = bin(reg[33])[2:].zfill(32)
    op = (ir[0:6])
    choices = {'000000': 'add', '000001': 'sub', '000010': 'mul', '000011': 'div', '000100': 'cmp', '000101': 'shl',
               '000110': 'shr', '000111': 'and', '001000': 'not', '001001': 'or', '001010': 'xor', '001011': 'push',
               '001100': 'pop', '010000': 'addi', '010001': 'subi', '010010': 'muli', '010011': 'divi', '010100': 'cmpi',
               '010101': 'andi','010110': 'noti', '010111': 'ori', '011000': 'xori', '011001': 'ldw', '011010': 'stw',
               '011011': 'ldb','011100': 'stb', '100000': 'bun', '100001': 'beq', '100010': 'blt', '100011': 'bgt',
               '100100': 'bne', '100101': 'ble', '100110': 'bge', '100111': 'bzd', '101000': 'bnz', '101001' : 'biv',
               '101010': 'bni', '110000': 'call', '110001': 'ret', '110010': 'isr', '110011' : 'reti', '111111': 'int'}
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
            f_output.write(prints(rx, ry, rz, result, '/') + '\n')
        reg[32] += 1
    elif result == 'cmp':
        montador()
        reg[32] += 1
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'shl':
        montador()
        aux = int(str(bin(reg[34])[2:].zfill(32)) + str(bin(reg[rx])[2:].zfill(32)), 2)
        reg[rz] = aux << (ry + 1)
        reg[rz] = calculate_er(reg[rz], 0, 0, result)
        f_output.write(prints(rx, ry, rz, result, '<<') + '\n')
        reg[32] += 1
    elif result == 'shr':
        montador()
        aux = int(str(bin(reg[34])[2:].zfill(32)) + str(bin(reg[rx])[2:].zfill(32)), 2)
        reg[rz] = aux >> (ry + 1)
        reg[rz] = calculate_er(reg[rz], 0, 0, result)
        f_output.write(prints(rx, ry, rz, result, '>>') + '\n')
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
            reg[rx] = calculate_er(reg[rx], reg[ry], rz, result)
            reg[rx] = int(float(int(reg[ry]) / int(rz)))
            f_output.write(prints(rx, ry, rz, result, '/') + '\n')
        except ZeroDivisionError:
            reg[rx] = calculate_er(reg[rx], reg[ry], rz, result)
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
    elif result == 'stw':
        montador()
        aux = reg[rx] + rz
        memory[aux] = reg[ry]
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
        if aux == 8224:
            aux = list(str(bin(reg[ry])[2:]).zfill(32))
            if aux[0] == '1':
                aux = str(bin(reg[ry])[2:]).zfill(32)
                watch_c = int(aux[1:32], 2) +1
                watch_ac = True
            elif aux[0] == '0':
                watch_ac = False
        if aux == 8707:
            aux2 = 0
            float_ac = True
            aux = str(bin(reg[ry])[2:]).zfill(32)
            float_op = aux[28:32]
            choices = {'0001' : 'add', '0010': 'sub', '0011': 'mul', '0100': 'div', '0101': 'atx',
                       '0110': 'aty', '0111': 'teto', '1000': 'piso', '1001': 'arrendodamento', '0000': 'nop'}
            result_float = choices.get(float_op, 'Não definido')
            if float_x_ac:
                x_spec = float_x
            else:
                x_spec = memory[8704]
            if float_y_ac:
                y_spec = float_y
            else:
                y_spec = memory[8705]
            if result_float == 'add':
                float_z = x_spec + y_spec
                memory[8706] = int(float_bin(float_z), 2)
                float_expo(float_bin(x_spec), float_bin(y_spec))
            elif result_float == 'sub':
                float_z = x_spec - y_spec
                memory[8706] = int(float_bin(float_z), 2)
                float_expo(float_bin(x_spec), float_bin(y_spec))
            elif result_float == 'mul':
                float_z = x_spec * y_spec
                memory[8706] = int(float_bin(float_z), 2)
                float_expo(float_bin(x_spec), float_bin(y_spec))
            elif result_float == 'div':
                try:
                    float_z = x_spec / y_spec
                    memory[8706] = int(float_bin(float_z), 2)
                    float_expo(float_bin(x_spec), float_bin(y_spec))
                except ZeroDivisionError:
                    aux2 = 1
                    float_c = 2
            elif result_float == 'atx':
                float_x = float_z
                float_x_ac = True
                memory[8704] = memory[8706]
                float_c = 2
            elif result_float == 'aty':
                float_y_ac = True
                float_y = float_z
                memory[8705] = memory[8706]
                float_c = 2
            elif result_float == 'teto':
                memory[8706] = math.ceil(float_z)
                float_c = 2
            elif result_float == 'piso':
                memory[8706] = math.floor(float_z)
                float_c = 2
            elif result_float == 'arrendodamento':
                memory[8706] = round(float_z)
                float_c = 2
            elif result_float == 'nop':
                a = a
            else:
                float_c = 2
                aux2 = 1
            if aux2 == 0:
                memory[8707] = 0
            else:
                aux2 = 0
                memory[8707] = 32
        reg[32] += 1
    elif result == 'ldb':
        #182617361873
        montador()
        indice = (reg[ry] + rz) % 4
        aux_ldb = str(bin(memory[int((reg[ry] + rz)/4)])[2:].zfill(32))
        if indice == 0:
            reg[rx] = int(aux_ldb[0:8], 2)
        elif indice == 1:
            reg[rx] = int(aux_ldb[8:16], 2)
        elif indice == 2:
            reg[rx] = int(aux_ldb[16:24], 2)
        elif indice == 3:
            reg[rx] = int(aux_ldb[24:32], 2)
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
        reg[32] += 1
    elif result == 'stb':
        montador()
        a = int((reg[rx] + rz) / 4)
        aux1 = list(str(bin(memory[a])[2:]).zfill(32))
        reg[ry] = str(bin(reg[ry])[2:].zfill(32))
        if ((reg[rx] + rz) % 4) == 0:
             aux1[0:8] = [reg[ry][24], reg[ry][25], reg[ry][26], reg[ry][27], reg[ry][28], reg[ry][29], reg[ry][30],
                          reg[ry][31]]
        elif ((reg[rx] + rz) % 4) == 1:
            aux1[8:16] = [reg[ry][24], reg[ry][25], reg[ry][26], reg[ry][27], reg[ry][28], reg[ry][29], reg[ry][30],
                          reg[ry][31]]
        elif ((reg[rx] + rz) % 4) == 2:
            aux1[16:24] = [reg[ry][24], reg[ry][25], reg[ry][26], reg[ry][27], reg[ry][28], reg[ry][29], reg[ry][30],
                          reg[ry][31]]
        elif ((reg[rx] + rz) % 4) == 3:
            aux1[24:32] = [reg[ry][24], reg[ry][25], reg[ry][26], reg[ry][27], reg[ry][28], reg[ry][29], reg[ry][30],
                          reg[ry][31]]
        reg[ry] = int(reg[ry], 2)
        memory[a] = ''.join(aux1)
        memory[a] = int(memory[a],2)
        if (a*4) == 34952:
            terminal = terminal + chr(reg[ry])
            terminal_ac = True
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
        reg[32] += 1
    elif result == 'bun':
        montador()
        reg[32] = rx
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'beq':
        montador()
        h = list(str(bin(reg[35])[2:]).zfill(32))
        if h[31] == '1':
            reg[32] = rx
        else:
            reg[32] = reg[32] + 1
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'blt':
        montador()
        h = list(str(bin(reg[35])[2:]).zfill(32))
        if h[30] == '1':
            reg[32] = rx
        else:
            reg[32] = reg[32] + 1
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'bgt':
        montador()
        h = list(str(bin(reg[35])[2:]).zfill(32))
        if h[29] == '1':
            reg[32] = rx
        else:
            reg[32] = reg[32] + 1
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'bne':
        montador()
        h = list(str(bin(reg[35])[2:]).zfill(32))
        if h[31] == '0':
            reg[32] = rx
        else:
            reg[32] = reg[32] + 1
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'ble':
        montador()
        h = list(str(bin(reg[35])[2:]).zfill(32))
        if h[31] == '1' or h[30] == '1':
            reg[32] = rx
        else:
            reg[32] = reg[32] + 1
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'bge':
        montador()
        h = list(str(bin(reg[35])[2:]).zfill(32))
        if h[31] == '1' or h[29] == '1':
            reg[32] = rx
        else:
            reg[32] = reg[32] + 1
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'bzd':
        montador()
        h = list(str(bin(reg[35])[2:]).zfill(32))
        if h[28] == '1':
            reg[32] = rx
        else:
            reg[32] = reg[32] + 1
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'bnz':
        montador()
        h = list(str(bin(reg[35])[2:]).zfill(32))
        if h[28] == '0':
            reg[32] = rx
        else:
            reg[32] = reg[32] + 1
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'biv':
        montador()
        h = list(str(bin(reg[35])[2:]).zfill(32))
        if h[26] == '1':
            reg[32] = rx
        else:
            reg[32] = reg[32] + 1
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'bni':
        montador()
        h = list(str(bin(reg[35])[2:]).zfill(32))
        if h[26] == '0':
            reg[32] = rx
        else:
            reg[32] = reg[32] + 1
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'call':
        montador()
        reg[rx] = reg[32] + 1
        reg[0] = 0
        reg[32] = reg[ry] + rz
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'ret':
        montador()
        reg[32] = reg[rx]
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'isr':
        montador()
        reg[rx] = reg[37]
        reg[ry] = reg[36]
        reg[32] = rz
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'reti':
        montador()
        reg[32] = reg[rx]
        inter_over = True
        soft_ac = False
    #  if watch_ac is False:
    #     if float_ac is False:
    #          aux = list(str(bin(reg[35])[2:]).zfill(32))
    #          aux[25] = '0'
    #          reg[35] = ''.join(aux)
    #          reg[35] = int(reg[35], 2)
        f_output.write(prints(rx, ry, rz, result, '') + '\n')
    elif result == 'int':
        montador()
        if rx == 0:
            reg[0] = 0
            reg[36] = 0
            reg[32] = 0
            f_output.write(prints(rx, ry, rz, result, '')+ '\n')
            if (terminal_ac):
                f_output.write('[TERMINAL] \n'+ terminal + '\n')
            f_output.write('[END OF SIMULATION]')
            break
        else:
            reg[37] = reg[32] + 1
            reg[36] = rx
            reg[32] = 3
            f_output.write(prints(rx, ry, rz, result, '') + '\n')
            f_output.write("[SOFTWARE INTERRUPTION]\n")
            soft_ac = True
    else:
        aux = list(str(bin(reg[35])[2:]).zfill(32))
        aux[26] = '1'
        reg[35] = ''.join(aux)
        reg[35] = int(reg[35], 2)
        reg[36] = reg[32]
        reg[37] = reg[32] + 1
        f_output.write('[INVALID INSTRUCTION @ 0x{}]\n'.format(hex(reg[32]*4)[2:].zfill(8).upper()))
        f_output.write("[SOFTWARE INTERRUPTION]\n")
        #soft_ac = True
        print(hex(reg[36]))
        reg[32] = 3
    if watch_ac:
        if watch_c > 0:
            watch_c = watch_c - 1
    if float_ac:
        if float_c > 0:
            float_c = float_c - 1

f_input.close()
f_output.close()