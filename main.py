import sys
import time

sys.path.insert(0, "bindings")  # Ensure Python can find the module
import audio_engine

# Initialize the audio engine
engine = audio_engine.AudioEngine()

# Access global control parameters
control_params = audio_engine.ControlParameters.getInstance()
control_params.setAnxiety(0.5)  # Set anxiety to 0.5 (mid-range)

# Create SynthWrapper instances
sine_synth = audio_engine.SynthWrapper()
square_synth = audio_engine.SynthWrapper()
tonic_square_synth = audio_engine.SynthWrapper()

# Register synthesizers with the audio engine
engine.registerSynth(sine_synth)
engine.registerSynth(square_synth)
engine.registerSynth(tonic_square_synth)

# Start audio playback
engine.start()

# Play MIDI notes
sine_synth.startNote(64, 0.5)  # E5 (MIDI note 76) with amplitude 0.5
time.sleep(1)
print("1")
control_params.setAnxiety(1)  # Set anxiety to 0.5 (mid-range)
sine_synth.startNote(65, 0.5)
time.sleep(1)
print("1")
control_params.setAnxiety(1)  # Set anxiety to 0.5 (mid-range)
sine_synth.startNote(63, 0.5)
time.sleep(1)

# square_synth.startNote(69, 0.5)  # A4 (MIDI note 69) with amplitude 0.5
# time.sleep(2)
# tonic_square_synth.startNote(64, 0.5)  # E4 (MIDI note 64) with amplitude 0.5

# time.sleep(2)

# Stop MIDI notes
sine_synth.stopNote()
square_synth.stopNote()
tonic_square_synth.stopNote()

# time.sleep(2)

# Stop audio playback
engine.stop()

