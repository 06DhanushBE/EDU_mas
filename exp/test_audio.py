#!/usr/bin/env python3
"""Test audio playback to diagnose sound issues"""

import sounddevice as sd
import numpy as np

print("=" * 60)
print("AUDIO DEVICE TEST")
print("=" * 60)

# List all devices
print("\nAvailable Audio Devices:\n")
devices = sd.query_devices()
print(devices)

print("\n" + "=" * 60)
print("Testing audio playback...")
print("=" * 60)

# Generate a test beep (440 Hz for 2 seconds)
duration = 2  # seconds
sample_rate = 24000
frequency = 440  # A note

t = np.linspace(0, duration, int(sample_rate * duration), False)
beep = np.sin(frequency * 2 * np.pi * t)

# Convert to int16 (like Cartesia audio)
beep_int16 = (beep * 32767).astype(np.int16)

print("\nPlaying test beep (440 Hz for 2 seconds)...")
print("You should hear a tone through your speakers\n")

try:
    sd.play(beep_int16, sample_rate)
    sd.wait()
    print("Test beep completed!")
    print("\nIf you heard the beep, your audio setup is working.")
    print("If not, check:")
    print("  1. Volume is turned up")
    print("  2. Speakers/headphones are connected")
    print("  3. Default audio device is correct")
except Exception as e:
    print(f"ERROR: Error playing audio: {e}")
    print("\nTry checking your audio device settings")
