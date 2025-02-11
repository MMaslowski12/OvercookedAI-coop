import numpy as np
import matplotlib.pyplot as plt

import os

# Get all files in logs directory
log_files = os.listdir('logs')

# Print contents of each npy file
for filename in log_files:
    filepath = os.path.join('logs', filename)
    print(f"\nContents of {filename}:")
    print("-" * 50)
    try:
        data = np.load(filepath)
        print(data)
    except Exception as e:
        print(f"Error loading {filename}: {e}")

# Load all data files
losses1 = np.load('logs/losses1.npy')
losses2 = np.load('logs/losses2.npy')
time_per_dataset = np.load('logs/time_per_dataset.npy')
time_per_training = np.load('logs/time_per_training.npy')
time_per_game = np.load('logs/time_per_game.npy')
file_sizes = np.load('logs/file_sizes.npy')
rewards = np.load('logs/rewards.npy')
game_counts = np.load('logs/game_counts.npy')
# time_per_experience = np.load('logs/time_per_experience.npy')
loss_distribution = np.load('logs/loss_distribution.npy')
# eps = np.load('logs/eps.npy')
# evals_rewards = np.load('logs/evals_rewards.npy')

# Print contents of all data files
print("\nContents of loss_distribution.npy:")
print("-" * 50)
try:
    loss_dist = np.load('logs/loss_distribution.npy')
    print(loss_dist)
except Exception as e:
    print(f"Error loading loss_distribution.npy: {e}")

print("\nContents of losses1.npy:")
print("-" * 50)
print(losses1)

print("\nContents of losses2.npy:") 
print("-" * 50)
print(losses2)

print("\nContents of rewards.npy:")
print("-" * 50)
print(rewards)

print("\nContents of game_counts.npy:")
print("-" * 50)
print(game_counts)

print("\nContents of time_per_training.npy:")
print("-" * 50)
print(time_per_training)

print("\nContents of time_per_game.npy:")
print("-" * 50)
print(time_per_game)

# print("\nContents of time_per_experience.npy:")
# print("-" * 50)
# print(time_per_experience)

print("\nContents of loss_distribution.npy:")
print("-" * 50)
print(loss_distribution)

# print("\nContents of eps.npy:")
# print("-" * 50)
# print(eps)

# print("\nEvals: rewards.npy:")
# print("-" * 50)
# print(evals_rewards)

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
