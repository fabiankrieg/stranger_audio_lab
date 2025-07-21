import time
import threading
import audio_engine
from stranger_midi_recorder import StrangerMidiRecorder


class StrangerPlayback:
    """
    A class to handle the playback of a song and record notes into a MIDI file, using an internal thread.

    Attributes:
        _song (StrangerSong): The song to be played.
        _engine (AudioEngine): The audio engine for playback.
        _synthesizers (dict): A dictionary of synthesizers registered with the audio engine.
        _current_part (StrangerPart): The current part of the song being played.
        _note_generator (StrangerNoteGenerator): The note generator for the current part.
        _is_playing (bool): Indicates whether playback is active.
        _midi_recorder (StrangerMidiRecorder): The MIDI recorder for recording notes.
    """

    def __init__(self, song, control_params):
        """
        Initializes the StrangerPlayback with a song and control parameters.

        Args:
            song (StrangerSong): The song to be played.
            control_params (ControlParameters): The control parameters for the audio engine.
        """
        self._song = song
        self._engine = audio_engine.AudioEngine(control_params)
        self._synthesizers = song.get_synthesizers()
        self._current_part = None
        self._note_generator = None
        self._is_playing = False
        self._thread = None

        # Initialize MIDI recorder
        bpm = 60 / song.get_update_interval()  # Convert update interval to BPM
        self._midi_recorder = StrangerMidiRecorder(bpm)

        # Register synthesizers with the audio engine
        for synth_name, synth in self._synthesizers.items():
            self._engine.registerSynth(synth_name, synth)

    def __del__(self):
        """
        Ensures the playback is stopped and the MIDI file is saved when the object is destroyed.
        """
        self.stop()

    def _playback_loop(self):
        """
        The internal playback loop that runs in a separate thread.
        """
        self._engine.start()
        self._current_part = self._song.get_next_part()
        self._note_generator = self._current_part.get_note_generator()
        self._is_playing = True

        print("Starting playback...")
        future_note_off_events = []

        while self._is_playing:
            loop_start_time = time.time()

            # Process future note off events
            for event in future_note_off_events[:]:
                event["remaining_subdivisions"] -= 1
                if event["remaining_subdivisions"] <= 0:
                    self._synthesizers[event["synth_name"]].stopNote()
                    self._midi_recorder.record_note_off(event["synth_name"], event["pitch"])
                    future_note_off_events.remove(event)

            # Get the next set of notes from the note generator
            notes = self._note_generator.get_next_notes()

            # Process note_start events
            for note_event in notes:
                synth_name = note_event["synth_name"]
                pitch = note_event["pitch"]
                amplitude = note_event["amplitude"]
                note_length = note_event["note_length"]

                # Start the note
                self._synthesizers[synth_name].startNote(pitch, amplitude)
                self._midi_recorder.record_note_on(synth_name, pitch, amplitude)

                # Schedule the note off event
                future_note_off_events.append({
                    "synth_name": synth_name,
                    "pitch": pitch,
                    "remaining_subdivisions": note_length,
                })

            # Check if the part has ended and transition if necessary
            if self._note_generator.get_part_end():
                next_part = self._song.get_next_part()
                if next_part == "end":
                    print("Song has ended.")
                    self.stop()
                    break
                elif next_part is not None:  # Repeat current part on None
                    print(f"Transitioning to part: {next_part.get_part_name()}")
                    self._current_part = next_part
                    self._note_generator = self._current_part.get_note_generator()

            loop_stop_time = time.time()
            sleep_duration = self._song.get_update_interval() - (loop_stop_time - loop_start_time)

            # Wait for the duration of the update interval before the next iteration
            if sleep_duration > 0:
                time.sleep(sleep_duration)
            else:
                print("Warning: Loop took longer than the update interval.")

    def start(self):
        """
        Starts playback in a separate thread.
        """
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._playback_loop)
            self._thread.start()

    def stop(self):
        """
        Stops playback and saves the MIDI file.
        """
        if self._is_playing:
            self._is_playing = False
            self._engine.stop()
            print("Playback stopped.")

            # Save the MIDI file
            self._midi_recorder.save(self._song.__class__.__name__)
        if self._thread is not None and self._thread.is_alive():
            self._thread.join()
