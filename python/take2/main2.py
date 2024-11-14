import numpy as np
from audiomentations import Compose, LoudnessNormalization, Limiter
import soundfile as sf

import os, glob
from pathlib import Path

def loudness_normalize_with_limiting(input_file, output_file, target_loudness=-23, limit_dbfs=-1):
    # Load audio file
    samples, sample_rate = sf.read(input_file)
    
    # Create augmentation pipeline
    augment = Compose([
        LoudnessNormalization(min_lufs=target_loudness,
                              max_lufs=target_loudness,
                              p=1.0),
        Limiter(min_threshold_db=limit_dbfs,
                max_threshold_db=limit_dbfs,
                min_attack=0.0001,
                max_attack=0.0001,
                min_release=0.05,
                max_release=0.05,
                threshold_mode='absolute',
                p=1.0)
    ])
    
    # Apply transformations
    augmented_samples = augment(samples=samples, sample_rate=sample_rate)
    
    # Save processed audio
    sf.write(output_file, augmented_samples, sample_rate)
    
    print(f"Processed audio saved to: {output_file}")

# Example usage
wav_files = glob.glob('../../data/*.wav')
for wav_file in wav_files:
    # remove .wav from filename
    filename = Path(wav_file).stem
    loudness_normalize_with_limiting(wav_file, f'{filename}_processed.wav', target_loudness=-23, limit_dbfs=-1)
