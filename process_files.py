import os
import shutil
import soundfile as sf
import numpy as np

# Define keywords for identifying lead and background vocals
lead_keywords = ['LeadVox', 'LeadVocal', 'LeadVoxDT', 'LeadVoxAlt']
background_keywords = ['BackingVox', 'BackingVoxDT', 'BackVox', 'BackingVocal']

def is_lead_vocal(filename):
    return any(keyword in filename for keyword in lead_keywords)

def is_background_vocal(filename):
    return any(keyword in filename for keyword in background_keywords)

def process_folder(folder):
    lead_vocals = []
    background_vocals = []

    # Collect lead and background vocal tracks
    for filename in os.listdir(folder):
        if filename.endswith('.wav'):
            if is_lead_vocal(filename):
                lead_vocals.append(filename)
            elif is_background_vocal(filename):
                background_vocals.append(filename)

    # Combine all background vocals into one track and store in the original folder
    background_mix_path = os.path.join(folder, 'background_vocals.wav')
    combine_background_vocals(folder, background_vocals, background_mix_path)

    if os.path.exists(background_mix_path):  # Check if the background mix was created
        # Process lead vocals based on their count
        if len(lead_vocals) > 1:
            original_lead_vocal = lead_vocals[-1]  # Use the last lead vocal for the original folder
            variant_lead_vocals = lead_vocals[:-1]  # Create variants with others

            for i, lead_vocal in enumerate(variant_lead_vocals):
                new_folder = f"{folder}_variant_{i+1}"
                os.makedirs(new_folder, exist_ok=True)
                shutil.copy(background_mix_path, os.path.join(new_folder, 'background_vocals.wav'))
                lead_path = os.path.join(new_folder, 'lead_vocals.wav')
                shutil.move(os.path.join(folder, lead_vocal), lead_path)
                create_mix(new_folder, lead_path, os.path.join(new_folder, 'background_vocals.wav'))

            lead_path = os.path.join(folder, 'lead_vocals.wav')
            os.rename(os.path.join(folder, original_lead_vocal), lead_path)
            create_mix(folder, lead_path, background_mix_path)
        elif lead_vocals:
            lead_path = os.path.join(folder, 'lead_vocals.wav')
            os.rename(os.path.join(folder, lead_vocals[0]), lead_path)
            create_mix(folder, lead_path, background_mix_path)
    else:
        print(f"No valid background vocal mix could be created in {folder}.")

def combine_background_vocals(source_folder, background_tracks, output_path):
    if not background_tracks:
        print(f"No background tracks found in {source_folder}.")
        return

    track_data = []
    max_length = 0
    samplerate = 0

    # Load all tracks and find the maximum length
    for track in background_tracks:
        data, rate = sf.read(os.path.join(source_folder, track))
        # Ensure all data is stereo for consistency
        if data.ndim == 1:  # Mono to Stereo conversion
            data = np.stack((data, data), axis=-1)
        track_data.append(data)
        max_length = max(max_length, data.shape[0])
        samplerate = rate  # Assuming all files have the same sample rate

    # Initialize an empty numpy array for mixing with two channels
    mixed = np.zeros((max_length, 2), dtype=np.float32)  # Make sure to handle stereo

    # Add each track to the mix, padding if necessary
    for data in track_data:
        if data.shape[0] < max_length:
            # Pad the array to match the max length
            padding_length = max_length - data.shape[0]
            data = np.pad(data, ((0, padding_length), (0, 0)), mode='constant')
        mixed += data

    # Normalize the mixed track to prevent clipping
    max_amp = np.max(np.abs(mixed))
    if max_amp > 1.0:
        mixed /= max_amp

    # Write the combined track to a file
    sf.write(output_path, mixed, samplerate)
    print(f"Combined background vocals written to {output_path}.")

def create_mix(folder, lead_path, background_path):
    lead_data, lead_rate = sf.read(lead_path)
    background_data, background_rate = sf.read(background_path)
    lead_length = len(lead_data) / lead_rate
    background_length = len(background_data) / background_rate
    print(f"Lead vocal length: {lead_length:.2f} seconds, Background vocal length: {background_length:.2f} seconds.")
    
    # Ensure both tracks have the same sample rate and channel count
    if lead_rate != background_rate:
        raise ValueError("Sample rates do not match. Cannot mix tracks.")

    # Convert mono to stereo if necessary
    if len(lead_data.shape) == 1:  # Mono lead
        lead_data = np.stack((lead_data, lead_data), axis=-1)
    if len(background_data.shape) == 1:  # Mono background
        background_data = np.stack((background_data, background_data), axis=-1)
    
    # Ensure both tracks are the same length
    min_length = min(len(lead_data), len(background_data))
    lead_data = lead_data[:min_length]
    background_data = background_data[:min_length]

    # Mix the two tracks
    mixed = lead_data + background_data
    max_amp = np.max(np.abs(mixed))
    
    # Normalize if necessary to prevent clipping
    if max_amp > 1.0:
        mixed /= max_amp

    sf.write(os.path.join(folder, 'mix.wav'), mixed, lead_rate)

if __name__ == "__main__":
    for folder in os.listdir('.'):
        if os.path.isdir(folder):
            process_folder(folder)

##################

import os
import shutil
import soundfile as sf
import numpy as np
import random

# Define keywords for identifying lead and background vocals
lead_keywords = ['LeadVox', 'LeadVocal', 'LeadVoxDT', 'LeadVoxAlt', 'lead_vocals']
background_keywords = ['BackingVox', 'BackingVoxDT', 'Vox', 'Vocal']

def is_lead_vocal(filename):
    return any(keyword in filename for keyword in lead_keywords)

def is_background_vocal(filename):
    return any(keyword in filename for keyword in background_keywords)

def process_folder(folder, dataset_backgrounds):
    lead_vocals = []
    background_vocals = []

    # Collect lead and background vocal tracks
    for filename in os.listdir(folder):
        if filename.endswith('.wav'):
            if is_lead_vocal(filename):
                lead_vocals.append(filename)
            elif is_background_vocal(filename):
                background_vocals.append(filename)

    # Combine all background vocals into one track and store in the original folder
    background_mix_path = os.path.join(folder, 'background_vocals.wav')
    combine_background_vocals(folder, background_vocals, background_mix_path)

    if os.path.exists(background_mix_path):
        if len(lead_vocals) > 1:
            original_lead_vocal = lead_vocals[-1]  # Use the last lead vocal for the original folder
            variant_lead_vocals = lead_vocals[:-1]  # Create variants with others

            for i, lead_vocal in enumerate(variant_lead_vocals):
                new_folder = f"{folder}_variant_{i+1}"
                os.makedirs(new_folder, exist_ok=True)
                shutil.copy(background_mix_path, os.path.join(new_folder, 'background_vocals.wav'))
                lead_path = os.path.join(new_folder, 'lead_vocals.wav')
                shutil.move(os.path.join(folder, lead_vocal), lead_path)
                create_mix(new_folder, lead_path, os.path.join(new_folder, 'background_vocals.wav'))
                create_random_variants(lead_path, dataset_backgrounds, new_folder)

            lead_path = os.path.join(folder, 'lead_vocals.wav')
            os.rename(os.path.join(folder, original_lead_vocal), lead_path)
            create_mix(folder, lead_path, background_mix_path)
            create_random_variants(lead_path, dataset_backgrounds, folder)
        elif lead_vocals:
            lead_path = os.path.join(folder, 'lead_vocals.wav')
            os.rename(os.path.join(folder, lead_vocals[0]), lead_path)
            create_mix(folder, lead_path, background_mix_path)
            create_random_variants(lead_path, dataset_backgrounds, folder)
    else:
        print(f"No valid background vocal mix could be created in {folder}.")

def create_random_variants(lead_vocal_path, dataset_backgrounds, folder):
    bg_count = len(dataset_backgrounds)

    # Allow sampling with replacement if there aren't enough background tracks
    if bg_count == 0:
        print(f"No background tracks found for {folder}. Skipping variant creation.")
        return

    # Create 3 variant folders with 1 random background vocal (with replacement)
    for i in range(3):
        random_bgs = random.choices(dataset_backgrounds, k=1)  # Sample with replacement
        create_variant(folder, lead_vocal_path, random_bgs, f"{folder}_random_1_bg_{i+1}")

    # Create 2 variant folders with 2 random background vocals (with replacement)
    for i in range(2):
        random_bgs = random.choices(dataset_backgrounds, k=2)
        create_variant(folder, lead_vocal_path, random_bgs, f"{folder}_random_2_bgs_{i+1}")

    # Create 1 variant folder with 3 random background vocals (with replacement)
    random_bgs = random.choices(dataset_backgrounds, k=3)
    create_variant(folder, lead_vocal_path, random_bgs, f"{folder}_random_3_bgs")

def create_variant(base_folder, lead_vocal_path, background_tracks, new_folder):
    os.makedirs(new_folder, exist_ok=True)
    
    # Mix the lead vocal with the randomly chosen background tracks
    background_mix_path = os.path.join(new_folder, 'background_vocals.wav')
    combine_background_vocals(os.path.dirname(lead_vocal_path), background_tracks, background_mix_path)
    
    # Check if the background mix file was created successfully
    if not os.path.exists(background_mix_path):
        print(f"Error: Background mix file {background_mix_path} was not created.")
        return
    
    lead_vocal_dest = os.path.join(new_folder, 'lead_vocals.wav')
    shutil.copy(lead_vocal_path, lead_vocal_dest)
    
    # Trim all tracks to the same length before mixing
    create_mix(new_folder, lead_vocal_dest, background_mix_path)

def create_mix(folder, lead_path, background_path):
    if not os.path.exists(lead_path):
        print(f"Error: Lead vocal file {lead_path} does not exist.")
        return
    
    if not os.path.exists(background_path):
        print(f"Error: Background vocal file {background_path} does not exist.")
        return

    lead_data, lead_rate = sf.read(lead_path)
    background_data, background_rate = sf.read(background_path)

    lead_length = len(lead_data) / lead_rate
    background_length = len(background_data) / background_rate
    print(f"Lead vocal length: {lead_length:.2f} seconds, Background vocal length: {background_length:.2f} seconds.")

    # Resample background if sample rates do not match
    if lead_rate != background_rate:
        print(f"Resampling background vocals from {background_rate} Hz to {lead_rate} Hz")
        background_data_left = librosa.resample(background_data[:, 0], orig_sr=background_rate, target_sr=lead_rate)
        background_data_right = librosa.resample(background_data[:, 1], orig_sr=background_rate, target_sr=lead_rate)
        background_data = np.stack([background_data_left, background_data_right], axis=-1)

    # Convert mono to stereo if necessary
    if len(lead_data.shape) == 1:  # Mono lead
        lead_data = np.stack((lead_data, lead_data), axis=-1)
    if len(background_data.shape) == 1:  # Mono background
        background_data = np.stack((background_data, background_data), axis=-1)

    # Ensure both tracks are the same length
    min_length = min(len(lead_data), len(background_data))
    lead_data = lead_data[:min_length]
    background_data = background_data[:min_length]

    # Mix the two tracks
    mixed = lead_data + background_data
    max_amp = np.max(np.abs(mixed))

    # Normalize if necessary to prevent clipping
    if max_amp > 1.0:
        mixed /= max_amp

    # Save the mix
    sf.write(os.path.join(folder, 'mix.wav'), mixed, lead_rate)

def process_dataset_folders(dataset_path):
    dataset_backgrounds = []

    # Gather all background vocal tracks from the dataset
    for folder in os.listdir(dataset_path):
        full_path = os.path.join(dataset_path, folder)
        if os.path.isdir(full_path):
            for filename in os.listdir(full_path):
                if is_background_vocal(filename):
                    dataset_backgrounds.append(os.path.join(full_path, filename))

    # Debugging: print the collected background vocals
    print(f"Collected {len(dataset_backgrounds)} background vocal tracks from the dataset.")
    
    if not dataset_backgrounds:
        print("No background vocals found in the dataset. Skipping variant creation.")
        return  # Exit early if no background vocals are found

    # Process the test and train folders
    folder_path = os.path.join(dataset_path)
    if os.path.isdir(folder_path):
        for song_folder in os.listdir(folder_path):
            full_song_path = os.path.join(folder_path, song_folder)
            if os.path.isdir(full_song_path):
                process_folder(full_song_path, dataset_backgrounds)

def combine_background_vocals(source_folder, background_tracks, output_path):
    if not background_tracks:
        print(f"No background tracks found in {source_folder}.")
        return

    track_data = []
    max_length = 0
    samplerate = 0

    # Load all tracks and find the maximum length
    for track in background_tracks:
        if track.endswith('.wav'):  # Ensure only .wav files are processed
            try:
                data, rate = sf.read(os.path.join(source_folder, track))
                # Ensure all data is stereo for consistency
                if data.ndim == 1:  # Mono to Stereo conversion
                    data = np.stack((data, data), axis=-1)
                track_data.append(data)
                max_length = max(max_length, data.shape[0])
                samplerate = rate  # Assuming all files have the same sample rate
            except Exception as e:
                print(f"Error reading {track}: {e}")
        else:
            print(f"Skipping non-audio file: {track}")

    if not track_data:
        print(f"No valid audio tracks found in {source_folder}.")
        return

    # Initialize an empty numpy array for mixing with two channels
    mixed = np.zeros((max_length, 2), dtype=np.float32)  # Make sure to handle stereo

    # Add each track to the mix, padding if necessary
    for data in track_data:
        if data.shape[0] < max_length:
            # Pad the array to match the max length
            padding_length = max_length - data.shape[0]
            data = np.pad(data, ((0, padding_length), (0, 0)), mode='constant')
        mixed += data

    # Normalize the mixed track to prevent clipping
    max_amp = np.max(np.abs(mixed))
    if max_amp > 1.0:
        mixed /= max_amp

    # Write the combined track to a file
    sf.write(output_path, mixed, samplerate)
    print(f"Combined background vocals written to {output_path}.")

import librosa

if __name__ == "__main__":
    dataset_path = '/home/ubuntu/ziploader/downloaded/dataset/unzipped/test'
    process_dataset_folders(dataset_path)