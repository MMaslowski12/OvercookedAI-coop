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

print(f"Total training time: {time_per_training}")
print(f"Number of games: {len(time_per_game)}")
print(f"Total time per game: {np.sum(time_per_game):.2f}s")
print(f"GAME COUNTS: {game_counts}")
# Calculate and print average time per game and rewards per game
print("\nGame Statistics:")
print("-" * 50)
print(f"Average time per game: {np.mean(time_per_game):.2f}s")
print(f"Average reward per game: {np.mean(rewards):.2f}")


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
