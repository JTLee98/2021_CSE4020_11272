import numpy as np 

#A
M = np.arange(2, 27)
print(M)

#B
M = M.reshape((5,5))
print(M)

#C
M[1:M.shape[0]-1, 1:M.shape[1]-1] = 0
print(M)

#D
M = M @ M
print(M)

#E
vmag = np.sqrt(np.add.reduce(M[0,:]**2))
print(vmag)
