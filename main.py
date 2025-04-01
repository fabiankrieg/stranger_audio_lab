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

# Play notes with fall-off
synth1.setFrequency(440.0)  # A4
synth1.setFallOff(0.99)     # Slow fall-off
synth1.noteOn()
synth2.setFrequency(660.0)  # E5
synth2.setFallOff(0.95)     # Faster fall-off
synth2.noteOn()
time.sleep(2)
synth1.noteOff()
time.sleep(2)

synth2.noteOff()

# Stop audio playback
engine.stop()

