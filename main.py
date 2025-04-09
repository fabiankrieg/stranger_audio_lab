import sys
import time

sys.path.insert(0, "bindings")
import audio_engine

# Initialize the audio engine
engine = audio_engine.AudioEngine()

# Create ControlParameters and add parameters
control_params = audio_engine.ControlParameters()
control_params.addParameter("attack_control", 0.05)
control_params.addParameter("decay_control", 0.1)

# Create and configure synthesizers using ControlParameters
square_synth = audio_engine.TonicSimpleADSRFilterSynth("SquareWave", control_params, "attack_control", "decay_control", 0.6, 0.4, 250.0, 1.0)
saw_synth = audio_engine.TonicSimpleADSRFilterSynth("SawtoothWave", control_params, "attack_control", "decay_control", 0.8, 0.6, 200.0, 0.8)

# Register synthesizers with the audio engine
engine.registerSynth(square_synth)
engine.registerSynth(saw_synth)

# Start audio playback
engine.start()

# Play MIDI notes
square_synth.startNote(64, 0.5)  # E4
time.sleep(1)
saw_synth.startNote(67, 0.5)  # G4
time.sleep(1)

# Dynamically modify parameters
print("Modifying attack_control to 0.1 and decay_control to 0.2")
control_params.addParameter("attack_control", 0.1)
control_params.addParameter("decay_control", 0.2)
time.sleep(1)

print("Modifying attack_control to 0.2 and decay_control to 0.3")
control_params.addParameter("attack_control", 0.2)
control_params.addParameter("decay_control", 0.3)
time.sleep(1)

# Stop MIDI notes
square_synth.stopNote()
saw_synth.stopNote()

# Stop audio playback
engine.stop()

