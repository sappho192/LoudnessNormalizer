import soundfile as sf
import pyloudnorm as pyln
import numpy as np
from cylimiter import Limiter

import os, glob
from pathlib import Path

def dbfs_to_threshold(dbfs_value):
    """
    Convert dBFS to a threshold value between 0 and 1.
    
    :param dbfs_value: dBFS value to convert
    :return: Threshold value between 0 and 1
    """
    return 10 ** (dbfs_value / 20)

def loudness_normalize_with_limiting(input_file, output_file, target_loudness=-23, limit_threshold=0.95):
    # Load audio file
    data, rate = sf.read(input_file)
    
    # Create Meter object
    meter = pyln.Meter(rate)
    
    # Calculate integrated loudness
    current_loudness = meter.integrated_loudness(data)
    
    print(f"Current loudness: {current_loudness:.2f} LUFS")
    
    # Normalize audio
    normalized_audio = pyln.normalize.loudness(data, current_loudness, target_loudness)
    
    # Apply limiter
    limiter = Limiter(threshold=limit_threshold)
    limited_audio = limiter.limit(normalized_audio)

    print(f'Normalized loudness: {meter.integrated_loudness(limited_audio):.2f} LUFS')
    
    # Save processed audio
    sf.write(output_file, limited_audio, rate)
    
    print(f"Processed audio saved to: {output_file}")

# Example usage

# print(f'-0.5dBFS = {dbfs_to_threshold(-0.5)}')
# print(f'-1dBFS = {dbfs_to_threshold(-1)}')
# print(f'-3dBFS = {dbfs_to_threshold(-3)}')
# print(f'-6dBFS = {dbfs_to_threshold(-6)}')
# loudness_normalize_with_limiting(input_file, output_file)

wav_files = glob.glob('../../data/*.wav')
for wav_file in wav_files:
    # remove .wav from filename
    filename = Path(wav_file).stem
    loudness_normalize_with_limiting(wav_file, f'{filename}_processed.wav')