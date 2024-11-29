import numpy as np
source venv/bin/activate

# Load the numpy file
file_path = 'losses.npy'
losses = np.load(file_path)

x = np.arange(len(losses))


plt.figure(figsize=(10, 6))
plt.plot(x, losses, label='Training Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.yscale('log')
plt.title('Training Loss Curve')
plt.legend()
plt.grid(True)
plt.show()

# Load each numpy file and calculate the average using the correct path in the current directory
file_paths = {
    "time_actions": "time_actions.npy",
    "time_saving": "time_saving.npy",
    "time_training": "time_training.npy",
    "total_time": "total_time.npy"
}

averages = {}

for key, path in file_paths.items():
    data = np.load(path)
    averages[key] = np.mean(data)

# Print the average for each file
print("XDDDDD")
for key, avg in averages.items():
    print(f"Average for {key}: {avg:.2f}")