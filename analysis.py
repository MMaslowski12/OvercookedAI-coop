import numpy as np
import matplotlib.pyplot as plt


losses = np.load('losses.npy')
print("LOSSES: ", losses)
print("TRAINS DONE: ", len(losses))

file_sizes = np.load('file_sizes.npy')
print("FILE SIZES:", file_sizes)    
print("GAMES PLAYED: ", len(file_sizes))

# Plotting the data
plt.figure(figsize=(8, 5))  # Optional: adjust figure size
plt.plot(losses, marker='o', linestyle='-', color='b', label='Data Points')
plt.title('Losses')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.yscale('log')
plt.grid(True)  # Optional: add grid
plt.legend()  # Optional: add legend
plt.tight_layout()  # Optional: adjust layout
plt.show()
