import sys
import time
import random

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
control_params.linkParameter("square_synth", "pitchBend", "pitchbend")
control_params.linkParameter("saw_synth", "pitchBend", "pitchbend")

# Start audio playback
engine.start()

# Global BPM and note duration calculation
global_bpm = 120  # Beats per minute
max_division = 16  # Maximum division for note duration (e.g., 16th notes == 16 divisions)
min_note_duration = 60 / global_bpm / (max_division / 4)  # Duration of the smallest note in seconds

# GeneratorLoop
print("Starting GeneratorLoop...")
try:
    while True:
        loop_start_time = time.time()

        # Generate random MIDI pitches for the synthesizers
        square_pitch = random.randint(60, 72)  # Random pitch between C4 and C5
        saw_pitch = random.randint(60, 72)

        # Stop notes
        square_synth.stopNote()
        saw_synth.stopNote()

        # Start notes
        square_synth.startNote(square_pitch, 0.5)  # Start square_synth note
        saw_synth.startNote(saw_pitch, 0.5)  # Start saw_synth note

        loop_stop_time = time.time()
        sleep_duration = min_note_duration - (loop_stop_time - loop_start_time)

        # Wait for the duration of the smallest note before the next iteration
        if sleep_duration > 0:
            time.sleep(sleep_duration)
        else:
            print("Warning: Loop took longer than the note duration, it took " + str(loop_stop_time - loop_start_time) + " seconds.")

except KeyboardInterrupt:
    print("Stopping GeneratorLoop...")

# Stop audio playback
engine.stop()

