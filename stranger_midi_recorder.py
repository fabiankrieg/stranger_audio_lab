from datetime import datetime
from mido import Message, MidiFile, MidiTrack, MetaMessage, second2tick
import time


class StrangerMidiRecorder:
    """
    A class to handle MIDI recording for a song.

    Attributes:
        _midi_file (MidiFile): The MIDI file to record notes.
        _midi_track (MidiTrack): The MIDI track to store note events.
        _last_event_time (float): The timestamp of the last MIDI event.
        _synth_channels (dict): A mapping of synthesizer names to unique MIDI channels.
        _next_channel (int): The next available MIDI channel.
        _ticks_per_beat (int): The number of ticks per beat in the MIDI file.
        _tempo (int): The tempo in microseconds per beat.
    """

    def __init__(self, bpm):
        """
        Initializes the StrangerMidiRecorder with the song's BPM.

        Args:
            bpm (float): The beats per minute of the song.
        """
        self._ticks_per_beat = 480  # Standard ticks per beat for compatibility with most players
        self._midi_file = MidiFile(ticks_per_beat=self._ticks_per_beat)
        self._midi_track = MidiTrack()
        self._midi_file.tracks.append(self._midi_track)
        self._last_event_time = None
        self._synth_channels = {}
        self._next_channel = 0  # MIDI channels range from 0 to 15
        self._tempo = int(60_000_000 / bpm)  # Convert BPM to microseconds per beat

        # Set the tempo in the MIDI file
        self._midi_track.append(MetaMessage('set_tempo', tempo=self._tempo))

    def _get_channel(self, synth_name):
        """
        Retrieves or assigns a unique MIDI channel for a synthesizer.

        Args:
            synth_name (str): The name of the synthesizer.

        Returns:
            int: The assigned MIDI channel.
        """
        if synth_name not in self._synth_channels:
            if self._next_channel > 15:
                raise ValueError("Exceeded the maximum number of MIDI channels (16).")
            self._synth_channels[synth_name] = self._next_channel
            self._next_channel += 1
        return self._synth_channels[synth_name]

    def record_midi(self, notes):
        """
        Records MIDI events for the given notes.

        Args:
            notes (list): A list of note events to record.
        """
        current_time = time.time()
        if self._last_event_time is None:
            self._last_event_time = current_time
        elapsed_time = current_time - self._last_event_time
        midi_time = self._calculate_midi_time(elapsed_time)
        self._last_event_time = current_time

        # Separate note_stop and note_start events
        note_stop_events = []
        note_start_events = []
        for note_event in notes:
            for synth_name, event in note_event.items():
                if event["event"] == "note_stop":
                    note_stop_events.append((synth_name, event))
                elif event["event"] == "note_start":
                    note_start_events.append((synth_name, event))

        # Record note_stop events first
        for synth_name, event in note_stop_events:
            channel = self._get_channel(synth_name)
            self._midi_track.append(Message('note_off', note=event["pitch"], velocity=0, time=midi_time, channel=channel))
            midi_time = 0  # Reset time for subsequent events in the same loop

        # Record note_start events
        for synth_name, event in note_start_events:
            channel = self._get_channel(synth_name)
            velocity = int(event["amplitude"] * 127)  # Convert amplitude to MIDI velocity
            self._midi_track.append(Message('note_on', note=event["pitch"], velocity=velocity, time=midi_time, channel=channel))
            midi_time = 0  # Reset time for subsequent events in the same loop

    def save(self, class_name):
        """
        Saves the MIDI file with a unique filename based on the class name and current date-time.

        Args:
            class_name (str): The name of the song's class.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{class_name}_{timestamp}.mid"
        self._midi_file.save(filename)
        print(f"MIDI file saved as {filename}.")

    def _calculate_midi_time(self, elapsed_time):
        """
        Converts elapsed time in seconds to MIDI ticks using mido.second2tick.

        Args:
            elapsed_time (float): The elapsed time in seconds.

        Returns:
            int: The elapsed time in MIDI ticks.
        """
        return int(second2tick(elapsed_time, self._ticks_per_beat, self._tempo))
