import numpy as np
import matplotlib.pyplot as plt


losses1 = np.load('losses1.npy')
losses2 = np.load('losses2.npy')
print("LOSSES: ", losses1)
print("TRAINS DONE: ", len(losses1))

file_sizes = np.load('file_sizes.npy')
print("FILE SIZES:", file_sizes)    
print("GAMES PLAYED: ", len(file_sizes))

# Plotting the data
plt.figure(figsize=(8, 5))  # Optional: adjust figure size
plt.plot(losses1, marker='o', linestyle='-', color='red', label='loss1')
plt.plot(losses2, marker='o', linestyle='-', color='blue', label='loss2')
plt.title('Losses')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.yscale('log')
plt.grid(True)  # Optional: add grid
plt.legend()  # Optional: add legend
plt.tight_layout()  # Optional: adjust layout
plt.show()
