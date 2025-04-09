import sys
import time

sys.path.insert(0, "bindings")
import audio_engine

# Create ControlParameters
control_params = audio_engine.ControlParameters()

# Initialize the audio engine with ControlParameters
engine = audio_engine.AudioEngine(control_params)

# Create and configure synthesizers
square_synth = audio_engine.TonicSimpleADSRFilterSynth("SquareWave", 0.05, 0.1, 0.6, 0.4, 250.0, 1.0)
saw_synth = audio_engine.TonicSimpleADSRFilterSynth("SawtoothWave", 0.05, 0.1, 0.6, 0.4, 250.0, 1.0)

# Register synthesizers with the audio engine and link parameters
engine.registerSynth("square_synth", square_synth)
engine.registerSynth("saw_synth", saw_synth)
#control_params.linkParameter("square_synth", "attack_control")
#control_params.linkParameter("square_synth", "decay_control")
control_params.linkParameter("square_synth", "pitchBend", "pitchbend")
control_params.linkParameter("saw_synth", "pitchBend", "pitchbend")

# Start audio playback
engine.start()

# Play MIDI notes
square_synth.startNote(64, 0.5)  # E4
time.sleep(1)
saw_synth.startNote(67, 0.5)  # G4
time.sleep(1)

# Smoothly transition pitchbend from 0 to 12 (E5 to E6) over 10 seconds
print("Transitioning pitchbend from 0 to 12 (E5 to E6) over 10 seconds")
for i in range(11):
    pitchbend_value = i * 1.2  # Increment pitchbend value
    control_params.updateParameter("pitchbend", pitchbend_value)  # Update pitchbend dynamically
    time.sleep(1)

# Dynamically modify parameters
print("Modifying attack_control to 0.1 and decay_control to 0.2")
control_params.updateParameter("attack_control", 0.1)
control_params.updateParameter("decay_control", 0.2)
time.sleep(1)

print("Modifying attack_control to 0.2 and decay_control to 0.3")
control_params.updateParameter("attack_control", 0.2)
control_params.updateParameter("decay_control", 0.3)
time.sleep(1)

# Stop MIDI notes
square_synth.stopNote()
saw_synth.stopNote()

# Stop audio playback
engine.stop()

