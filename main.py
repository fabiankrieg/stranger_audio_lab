import sys
import time

sys.path.insert(0, "bindings")  # Ensure Python can find the module
import audio_engine

# Initialize the audio engine
engine = audio_engine.AudioEngine()

# Create Tonic synthesizers
sine_synth = audio_engine.Synth()
sine_synth.setRectWave(660.0)  # E5

square_synth = audio_engine.Synth()
square_synth.setRectWave(440.0)  # A4

tonic_square_synth = audio_engine.Synth()
tonic_square_synth.setRectWave(330.0)  # E4

# Register synthesizers with the audio engine
engine.registerSynth(sine_synth)
engine.registerSynth(square_synth)
engine.registerSynth(tonic_square_synth)

# Start audio playback
engine.start()

# Play notes (frequency already set)
time.sleep(2)

# Stop audio playback
engine.stop()

