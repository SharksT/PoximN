import collections
cache = collections.namedtuple('cache','v0 I0 ID0 data0 v1 I1 ID1 data1')

# rx + im16 <= Cache ldb,stb,stw,ldw
# cache pc <= data[1..3] (1 ao 4) , line[3..6] (5 ao 7), id[7..32]

cacheD,cacheI = [8],[8]
cacheprep = cache(0,0,0,[0,0,0,0],0,0,0,[0,0,0,0])
for i in range(8):
    cacheD.append(cacheprep)
    cacheI.append(cacheprep)

print(cacheD[2].v1)