import numpy as np

losses = np.load('losses.npy')
print("LOSSES: ", losses)
print("TRAINS DONE: ", len(losses))

file_sizes = np.load('file_sizes.npy')
print("FILE SIZES:", file_sizes)    
print("GAMES PLAYED: ", len(file_sizes))
    