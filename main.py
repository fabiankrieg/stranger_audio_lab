import sys
import time
import random

sys.path.insert(0, "bindings")  # Ensure Python can find the module
import audio_engine

import time

engine = audio_engine.AudioEngine()

# Change frequency in real time
engine.setFrequency(880.0)  # A4 -> A5
time.sleep(2)

engine.setFrequency(440.0)  # Back to A4
time.sleep(2)

