import soundfile as sf
import pyloudnorm as pyln
import numpy as np
from cylimiter import Limiter
import noisereduce as nr

import os, glob
from pathlib import Path

def dbfs_to_threshold(dbfs_value):
    """
    Convert dBFS to a threshold value between 0 and 1.
    
    :param dbfs_value: dBFS value to convert
    :return: Threshold value between 0 and 1
    """
    return 10 ** (dbfs_value / 20)

def loudness_normalize_with_limiting(input_file, output_file, target_loudness, noise_file=None):
    # Load audio file
    data, rate = sf.read(input_file)
    
    # Create Meter object
    meter = pyln.Meter(rate)

    if (noise_file != None):
        data_noise, rate_noise = sf.read(noise_file)
        print("processing stationary noise reduction")
        data = nr.reduce_noise(y = data, sr=rate_noise, stationary=True, y_noise=data_noise, prop_decrease=0.95)
        # sf.write(output_file, data, rate)
        # return
    else:
        print("processing non-stationary noise reduction")
        data = nr.reduce_noise(y = data, sr=rate, stationary=False, prop_decrease=0.95)
    
    # Calculate integrated loudness
    current_loudness = meter.integrated_loudness(data)
    
    print(f"Current loudness: {current_loudness:.2f} LUFS")

    # Get gain required to reach target loudness
    gain = target_loudness - current_loudness
    
    # Apply limiter first
    print(f"Limiter threshold: {-1 * gain:.2f} LUFS")
    target_threshold = dbfs_to_threshold((-1 * gain))
    limiter = Limiter(threshold=target_threshold)
    limited_audio = limiter.limit(data)
    
    # Normalize audio
    normalized_audio = pyln.normalize.loudness(limited_audio, current_loudness, target_loudness)
    
    print(f'Normalized loudness: {meter.integrated_loudness(normalized_audio):.2f} LUFS')
    
    # Save processed audio
    sf.write(output_file, normalized_audio, rate)
    
    print(f"Processed audio saved to: {output_file}")

# Example usage

# print(f'-0.5dBFS = {dbfs_to_threshold(-0.5)}')
# print(f'-1dBFS = {dbfs_to_threshold(-1)}')
# print(f'-3dBFS = {dbfs_to_threshold(-3)}')
# print(f'-6dBFS = {dbfs_to_threshold(-6)}')
input_audio = "data/aaa"
input_noise = "data/aaa_noise.wav"
# loudness_normalize_with_limiting(f"{input_audio}.wav", f"{input_audio}_normalized.wav", -23, noise_file=input_noise)
loudness_normalize_with_limiting(f"{input_audio}.wav", f"{input_audio}_normalized.wav", -23, noise_file=None)

# wav_files = glob.glob('data/*.wav', recursive=True)
# for wav_file in wav_files:
#     # remove .wav from filename
#     filename = Path(wav_file).stem
#     if not os.path.exists('normalized'):
#         os.makedirs('normalized')
#     loudness_normalize_with_limiting(wav_file, f'normalized/{filename}_normalized_-23LUFS.wav', target_loudness=-23)