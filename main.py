import sys
import time

sys.path.insert(0, "bindings")  # Ensure Python can find the module
import audio_engine

# Initialize the audio engine and synthesizer
engine = audio_engine.AudioEngine()
synth = engine.getSynth()

# Start audio playback
engine.start()

# Change frequency in real time
synth.setFrequency(880.0)  # A4 -> A5
time.sleep(2)

synth.setFrequency(440.0)  # Back to A4
time.sleep(2)

synth.setFrequency(660.0)  # E5
time.sleep(2)

# Stop audio playback
engine.stop()

