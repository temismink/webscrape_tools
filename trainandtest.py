import os
import shutil
import random

# Define the root directory containing the song folders
root_directory = '/home/ubuntu/ziploader/downloaded/dataset/unzipped'
train_dir = os.path.join(root_directory, 'train')
test_dir = os.path.join(root_directory, 'test')

def split_folders(ratio=0.8):
    """Split the song folders into train and test directories based on a ratio."""
    # Ensure the train and test directories exist
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)

    # List all folders in the root directory
    folders = [f for f in os.listdir(root_directory) if os.path.isdir(os.path.join(root_directory, f))]
    
    # Shuffle the list of folders to ensure random distribution
    random.shuffle(folders)
    
    # Calculate the split index
    split_index = int(len(folders) * ratio)
    
    # Assign folders to train and test sets
    train_folders = folders[:split_index]
    test_folders = folders[split_index:]

    # Move folders to the respective train and test directories
    for folder in train_folders:
        shutil.move(os.path.join(root_directory, folder), train_dir)
    
    for folder in test_folders:
        shutil.move(os.path.join(root_directory, folder), test_dir)

    print(f"Moved {len(train_folders)} folders to {train_dir}")
    print(f"Moved {len(test_folders)} folders to {test_dir}")

if __name__ == "__main__":
    split_folders()  # You can pass a different ratio if needed, e.g., split_folders(0.7)
