#create a script to make sure each file in 
import os
import soundfile as sf
import numpy as np

def match_length_and_save(data, target_length, rate):
    """Trim or pad the data to match the target length."""
    if len(data) > target_length:
        # Trim to target length
        return data[:target_length]
    elif len(data) < target_length:
        # Pad with zeros to target length
        padding = np.zeros((target_length - len(data), data.shape[1]))
        return np.vstack((data, padding))
    return data

def ensure_same_length(folder):
    """Ensure that all tracks (lead_vocals.wav, background_vocals.wav, and mix.wav) have the same length."""
    lead_vocal_path = os.path.join(folder, 'lead_vocals.wav')
    background_vocal_path = os.path.join(folder, 'background_vocals.wav')
    mix_path = os.path.join(folder, 'mix.wav')

    # Check if all files exist
    if not (os.path.exists(lead_vocal_path) and os.path.exists(background_vocal_path) and os.path.exists(mix_path)):
        print(f"One or more tracks are missing in {folder}")
        return

    # Read all the audio files
    lead_data, lead_rate = sf.read(lead_vocal_path)
    background_data, background_rate = sf.read(background_vocal_path)
    mix_data, mix_rate = sf.read(mix_path)

    # Ensure that all files have the same sample rate
    if lead_rate != mix_rate or background_rate != mix_rate:
        print(f"Sample rates do not match in {folder}. Skipping.")
        return

    # Get the length of the mix (we want to match other files to this length)
    mix_length = len(mix_data)

    # Match the length of the lead vocals and background vocals to the mix length
    lead_data = match_length_and_save(lead_data, mix_length, lead_rate)
    background_data = match_length_and_save(background_data, mix_length, background_rate)

    # Write the corrected audio files back
    sf.write(lead_vocal_path, lead_data, lead_rate)
    sf.write(background_vocal_path, background_data, background_rate)

    print(f"Processed {folder}: ensured all tracks are {mix_length / mix_rate:.2f} seconds.")

def process_folders(base_path):
    """Process all song folders in the 'train', 'test', and 'valid' directories."""
    for dataset_folder in ['train', 'test', 'valid']:
        dataset_path = os.path.join(base_path, dataset_folder)

        # Check if the directory exists
        if not os.path.exists(dataset_path):
            print(f"{dataset_path} does not exist.")
            continue

        # Process each song folder in the dataset (train/test/valid)
        for song_folder in os.listdir(dataset_path):
            full_song_path = os.path.join(dataset_path, song_folder)
            if os.path.isdir(full_song_path):
                ensure_same_length(full_song_path)

if __name__ == "__main__":
    base_path = '/home/ubuntu/ziploader/downloaded/dataset/unzipped'
    process_folders(base_path)
