import numpy as np

losses = np.load('losses.npy')
print(losses)

file_sizes = np.load('file_sizes.npy')
print(file_sizes)



#WTF is this increasing? not flushed properly each game is ~ 145MB

#

for i in range (15):
    if ((i + 1) % 3) == 0:
        print("xd")
    print(i)
    