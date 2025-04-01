import sys
import time

sys.path.insert(0, "bindings")  # Ensure Python can find the module
import audio_engine

# Initialize the audio engine
engine = audio_engine.AudioEngine()

# Create multiple synthesizers
synth1 = audio_engine.SimpleSynth()
synth2 = audio_engine.SimpleSynth()

# Register synthesizers with the audio engine
engine.registerSynth(synth1)
engine.registerSynth(synth2)

# Start audio playback
engine.start()

# Change frequencies in real time
synth1.setFrequency(440.0)  # A4
synth2.setFrequency(660.0)  # E5
time.sleep(2)

synth1.setFrequency(880.0)  # A5
synth2.setFrequency(440.0)  # A4
time.sleep(2)

# Stop audio playback
engine.stop()

