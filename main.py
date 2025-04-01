import sys
import time

sys.path.insert(0, "bindings")  # Ensure Python can find the module
import audio_engine

# Initialize the audio engine
engine = audio_engine.AudioEngine()

# Create multiple synthesizers
sine_synth = audio_engine.SineSynth()
square_synth = audio_engine.SquareSynth()

# Register synthesizers with the audio engine
engine.registerSynth(sine_synth)
engine.registerSynth(square_synth)

# Start audio playback
engine.start()

# Play notes with fall-off
sine_synth.setFrequency(440.0)  # A4
sine_synth.setFallOff(200.0)    # 0.2 seconds fall-off
sine_synth.noteOn()
square_synth.setFrequency(660.0)  # E5
square_synth.setFallOff(1000.0)   # 1 second fall-off
square_synth.noteOn()
time.sleep(2)
sine_synth.noteOff()
time.sleep(2)

square_synth.noteOff()
time.sleep(2)

# Stop audio playback
engine.stop()

