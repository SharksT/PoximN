from dataclasses import dataclass
from typing import List
@dataclass
class Cache:
    v0: bool
    v1: bool
    i0: int
    i1: int
    data0: List[int]
    data1: List[int]

cacheI = []

for i in range(8):
    cacheI.append(Cache(False,False,0,0,[0,0,0,0],[0,0,0,0]))

print(cacheI[1])