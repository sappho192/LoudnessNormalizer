import soundfile as sf
import pyloudnorm as pyln
import numpy as np
from cylimiter import Limiter
import noisereduce as nr

import os, glob
from pathlib import Path

import time

class TimeResult:
    def __init__(self, name: str, duration: float):
        self.name = name
        self.duration = duration

    def __str__(self) -> str:
        return f"{self.name}: {self.duration:.2f} seconds"

def dbfs_to_threshold(dbfs_value):
    """
    Convert dBFS to a threshold value between 0 and 1.
    
    :param dbfs_value: dBFS value to convert
    :return: Threshold value between 0 and 1
    """
    return 10 ** (dbfs_value / 20)

def loudness_normalize_with_limiting(input_file, target_loudness, apply_nr=True, noise_prop_decrease=0.95, noise_file=None):
    # Load audio file
    data, rate = sf.read(input_file)
    input_file_stem = Path(input_file).absolute().parent / Path(input_file).stem
    
    # Create Meter object
    meter = pyln.Meter(rate)

    if (apply_nr == True):
        data = noise_reduction(noise_file, data, rate, noise_prop_decrease)
    
    # Calculate integrated loudness
    current_loudness = meter.integrated_loudness(data)
    
    print(f"Current loudness: {current_loudness:.2f} LUFS")

    # Get gain required to reach target loudness
    gain = target_loudness - current_loudness
    
    # Apply limiter first
    print(f"Limiter threshold: {-1 * gain:.2f} LUFS")
    target_threshold = dbfs_to_threshold((-1 * gain) - 1) # attenuate 1 more lufs
    limiter = Limiter(threshold=target_threshold)
    limited_audio = limiter.limit(data)
    current_loudness = meter.integrated_loudness(limited_audio)
    print(f"Current loudness: {current_loudness:.2f} LUFS")
    
    # Normalize audio
    normalized_audio = pyln.normalize.loudness(limited_audio, current_loudness, target_loudness)
    
    print(f'Normalized loudness: {meter.integrated_loudness(normalized_audio):.2f} LUFS')
    
    # Save processed audio
    output_file_suffix = "_normalized"
    if (apply_nr == True):
        if (noise_file != None): # Stationary NR
            output_file_suffix += f"_st_{noise_prop_decrease}"
        else: # Non-stationary NR
            output_file_suffix += f"_nst_{noise_prop_decrease}"
    output_filename = f"{input_file_stem}{output_file_suffix}.flac"
    sf.write(output_filename, normalized_audio, rate)
    
    print(f"Processed audio saved to: {output_filename}")

def noise_reduction(noise_file, data, audio_rate, prop_decrease):
    if (noise_file != None):
        data_noise, rate_noise = sf.read(noise_file)
        print("processing stationary noise reduction")
        data = nr.reduce_noise(y = data, sr=audio_rate, stationary=True, y_noise=data_noise, prop_decrease=prop_decrease)
    else:
        print("processing non-stationary noise reduction")
        data = nr.reduce_noise(y = data, sr=audio_rate, stationary=False, prop_decrease=prop_decrease)
    return data

# Example usage

# print(f'-0.5dBFS = {dbfs_to_threshold(-0.5)}')
# print(f'-1dBFS = {dbfs_to_threshold(-1)}')
# print(f'-3dBFS = {dbfs_to_threshold(-3)}')
# print(f'-6dBFS = {dbfs_to_threshold(-6)}')
input_audio = "data/aaa"
input_noise = "data/aaa_noise.wav"

start_time = time.perf_counter()
loudness_normalize_with_limiting(input_audio, -23, apply_nr=False, noise_file=None) # Normalization without NR
end_time = time.perf_counter()
benchmark_normalize = TimeResult("Normalize", end_time - start_time)

start_time = time.perf_counter()
loudness_normalize_with_limiting(input_audio, -23, apply_nr=True, noise_file=input_noise, noise_prop_decrease=0.8) # Stationary NR
end_time = time.perf_counter()
benchmark_normalize_nr = TimeResult("Normalize with Stationary NR", end_time - start_time)

start_time = time.perf_counter()
loudness_normalize_with_limiting(input_audio, -23, apply_nr=True, noise_file=None, noise_prop_decrease=0.85) # Non-stationary NR
end_time = time.perf_counter()
benchmark_normalize_nr_nst = TimeResult("Normalize with Non-stationary NR", end_time - start_time)

print(benchmark_normalize)
print(benchmark_normalize_nr)
print(benchmark_normalize_nr_nst)

# wav_files = glob.glob('data/*.wav', recursive=True)
# for wav_file in wav_files:
#     # remove .wav from filename
#     filename = Path(wav_file).stem
#     if not os.path.exists('normalized'):
#         os.makedirs('normalized')
#     loudness_normalize_with_limiting(wav_file, f'normalized/{filename}_normalized_-23LUFS.wav', target_loudness=-23)