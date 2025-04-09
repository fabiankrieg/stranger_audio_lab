import sys
import time

sys.path.insert(0, "bindings")
import audio_engine

# Initialize the audio engine
engine = audio_engine.AudioEngine()

# Create and configure synthesizers using the constructor
sine_synth = audio_engine.SynthWrapper("SineWave", 0.05, 0.1, 0.7, 0.5, 300.0, 1.2)
square_synth = audio_engine.SynthWrapper("SquareWave", 0.02, 0.2, 0.6, 0.4, 250.0, 1.0)
saw_synth = audio_engine.SynthWrapper("SawtoothWave", 0.03, 0.15, 0.8, 0.6, 200.0, 0.8)

# Register synthesizers with the audio engine
engine.registerSynth(sine_synth)
engine.registerSynth(square_synth)
engine.registerSynth(saw_synth)

# Start audio playback
engine.start()

# Play MIDI notes
sine_synth.startNote(60, 0.5)  # C4
time.sleep(1)
square_synth.startNote(64, 0.5)  # E4
time.sleep(1)
saw_synth.startNote(67, 0.5)  # G4
time.sleep(1)

# Stop MIDI notes
sine_synth.stopNote()
square_synth.stopNote()
saw_synth.stopNote()

# Stop audio playback
engine.stop()

