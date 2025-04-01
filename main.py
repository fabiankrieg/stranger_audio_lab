import sys
import time

sys.path.insert(0, "bindings/Debug")  # Ensure Python can find the module
import audio_engine

# Initialize the audio engine
engine = audio_engine.AudioEngine()

# Set the frequency to 440Hz (A4)
engine.setFrequency(440.0)

# Keep the audio engine running for 5 seconds to hear the sine wave
print("Playing 440Hz sine wave for 5 seconds...")
time.sleep(5)

print("Playback finished.")
