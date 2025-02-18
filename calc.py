import galois
from numpy import zeros, savetxt
import pandas as pd
order=2**24
print(order)
#GF = galois.GF(order, repr='int')
#mul_map = [[0 for i in range (order)] for _ in range (order)]
#add_map = [[0 for i in range (order)] for _ in range (order)]
#mul_map = zeros((order, order), 'int')
#add_map = zeros((order, order), 'int')
mul_map = pd.DataFrame(0, index=range(order), columns=range(order))
add_map = pd.DataFrame(0, index=range(order), columns=range(order))
def operation_mapping() -> None:
    for i in range(order):
        for j in range(order):
            op1, op2=GF(i), GF(j)
            mul_map[i][j]=int(op1*op2)
            add_map[i][j]=int(op1+op2)
operation_mapping()

savetxt('addmap.txt', add_map, fmt='%d')
savetxt('mulmap.txt', mul_map, fmt='%d')

