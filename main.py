import sys
import time

# Add bindings directory to the Python path
sys.path.insert(0, "./bindings")

from random_note_example import RandomNoteEnsemble
import audio_engine

# Create ControlParameters
control_params = audio_engine.ControlParameters()

# Initialize the RandomNoteEnsemble with ControlParameters and BPM
bpm = 120  # Beats per minute
ensemble = RandomNoteEnsemble(control_params, bpm)

# Retrieve the synthesizers and register them with the audio engine
engine = audio_engine.AudioEngine(control_params)
synthesizers = ensemble.get_synthesizers()
for synth_name, synth in synthesizers.items():
    engine.registerSynth(synth_name, synth)

# Start audio playback
engine.start()

# Retrieve the first part and its note generator
current_part = ensemble.get_first_part()
note_generator = current_part.get_note_generator()

# GeneratorLoop
print("Starting GeneratorLoop...")
try:
    while True:
        loop_start_time = time.time()

        # Get the next set of notes from the note generator
        notes = note_generator.get_next_notes()

        # Process each note event
        for note_event in notes:
            for synth_name, event in note_event.items():
                if event["event"] == "note_start":
                    pitch = event["pitch"]
                    amplitude = event["amplitude"]
                    synthesizers[synth_name].startNote(pitch, amplitude)
                elif event["event"] == "note_stop":
                    synthesizers[synth_name].stopNote()

        # Check if the part has ended and transition if necessary
        if note_generator.get_part_end():
            next_part_name = current_part.get_next_part()
            if next_part_name is not None:
                print(f"Transitioning to part: {next_part_name}")
                # Logic to transition to the next part can be implemented here

        loop_stop_time = time.time()
        sleep_duration = ensemble.get_update_interval() - (loop_stop_time - loop_start_time)

        # Wait for the duration of the update interval before the next iteration
        if sleep_duration > 0:
            time.sleep(sleep_duration)
        else:
            print("Warning: Loop took longer than the update interval.")

except KeyboardInterrupt:
    print("Stopping GeneratorLoop...")

# Stop audio playback
engine.stop()

