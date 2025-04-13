import sys
import time

# Add bindings directory to the Python path
sys.path.insert(0, "./bindings")

from example_random_note import RandomNoteSong
import audio_engine

# Create ControlParameters
control_params = audio_engine.ControlParameters()

# Initialize the RandomNoteSong with ControlParameters and BPM
bpm = 120  # Beats per minute
song = RandomNoteSong(control_params, bpm)

# Retrieve the synthesizers and register them with the audio engine
engine = audio_engine.AudioEngine(control_params)
synthesizers = song.get_synthesizers()
for synth_name, synth in synthesizers.items():
    engine.registerSynth(synth_name, synth)

# Start audio playback
engine.start()

# Retrieve the first part and its note generator
current_part = song.get_first_part()
note_generator = current_part.get_note_generator()

# GeneratorLoop
print("Starting GeneratorLoop...")
try:
    while True:
        loop_start_time = time.time()

        # Get the next set of notes from the note generator
        notes = note_generator.get_next_notes()

        # Separate note_end and note_start events
        note_end_events = []
        note_start_events = []
        for note_event in notes:
            for synth_name, event in note_event.items():
                if event["event"] == "note_end":
                    note_end_events.append((synth_name, event))
                elif event["event"] == "note_start":
                    note_start_events.append((synth_name, event))

        # Process note_end events first
        for synth_name, event in note_end_events:
            synthesizers[synth_name].stopNote()

        # Process note_start events
        for synth_name, event in note_start_events:
            pitch = event["pitch"]
            amplitude = event["amplitude"]
            synthesizers[synth_name].startNote(pitch, amplitude)

        # Check if the part has ended and transition if necessary
        if note_generator.get_part_end():
            next_part_name = current_part.get_next_part()
            if next_part_name == "end":
                print("Song has ended.")
                break
            elif next_part_name is not None:
                print(f"Transitioning to part: {next_part_name}")
                # Logic to transition to the next part can be implemented here

        loop_stop_time = time.time()
        sleep_duration = song.get_update_interval() - (loop_stop_time - loop_start_time)

        # Wait for the duration of the update interval before the next iteration
        if sleep_duration > 0:
            time.sleep(sleep_duration)
        else:
            print("Warning: Loop took longer than the update interval.")

except KeyboardInterrupt:
    print("Stopping GeneratorLoop...")

# Stop audio playback
engine.stop()

