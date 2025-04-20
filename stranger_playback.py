import time
import audio_engine

class StrangerPlayback:
    """
    A class to handle the playback of a song.

    Attributes:
        _song (StrangerSong): The song to be played.
        _engine (AudioEngine): The audio engine for playback.
        _synthesizers (dict): A dictionary of synthesizers registered with the audio engine.
        _current_part (StrangerPart): The current part of the song being played.
        _note_generator (StrangerNoteGenerator): The note generator for the current part.
        _is_playing (bool): Indicates whether playback is active.
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

        # Register synthesizers with the audio engine
        for synth_name, synth in self._synthesizers.items():
            self._engine.registerSynth(synth_name, synth)

    def __del__(self):
        """
        Ensures the playback is stopped when the object is destroyed.
        """
        self.stop_playback()

    def start_playback(self):
        """
        Starts the playback of the song.
        """
        self._engine.start()
        self._current_part = self._song.get_next_part()
        self._note_generator = self._current_part.get_note_generator()
        self._is_playing = True

        print("Starting playback...")
        while self._is_playing:
            loop_start_time = time.time()

            # Get the next set of notes from the note generator
            notes = self._note_generator.get_next_notes()

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
                self._synthesizers[synth_name].stopNote()

            # Process note_start events
            for synth_name, event in note_start_events:
                pitch = event["pitch"]
                amplitude = event["amplitude"]
                self._synthesizers[synth_name].startNote(pitch, amplitude)

            # Check if the part has ended and transition if necessary
            if self._note_generator.get_part_end():
                next_part = self._song.get_next_part()
                if next_part == "end":
                    print("Song has ended.")
                    self.stop_playback()
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

    def stop_playback(self):
        """
        Stops the playback of the song.
        """
        if self._is_playing:
            self._is_playing = False
            self._engine.stop()
            print("Playback stopped.")
